import os
import re
import time
import hashlib
from collections import Counter

# Vietnamese NLP
try:
    from underthesea import word_tokenize, pos_tag
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    UNDERTHESEA_AVAILABLE = False

# Vietnamese stopwords - common words that don't carry meaning
VN_STOPWORDS = {
    # Pronouns
    'tôi', 'tao', 'mình', 'ta', 'chúng_tôi', 'chúng_ta', 'bạn', 'cậu', 'anh', 'chị', 'em',
    'ông', 'bà', 'cô', 'chú', 'họ', 'nó', 'hắn', 'y', 'ấy', 'đó', 'này', 'kia',
    # Conjunctions & Prepositions
    'và', 'hoặc', 'hay', 'nhưng', 'mà', 'vì', 'nên', 'do', 'bởi', 'để', 'cho',
    'của', 'với', 'trong', 'ngoài', 'trên', 'dưới', 'từ', 'đến', 'về', 'theo',
    'qua', 'bằng', 'như', 'thì', 'là', 'được', 'bị', 'có', 'không', 'còn',
    # Auxiliary verbs & Modal verbs
    'sẽ', 'đã', 'đang', 'vẫn', 'cũng', 'rồi', 'mới', 'lại', 'nữa', 'thêm',
    'phải', 'cần', 'nên', 'muốn', 'có_thể', 'chắc', 'hẳn',
    # Question words
    'gì', 'nào', 'đâu', 'sao', 'ai', 'bao', 'nhiêu', 'mấy',
    # Demonstratives & Others
    'này', 'kia', 'ấy', 'đó', 'đây', 'nọ', 'thế', 'vậy', 'vâng', 'dạ',
    'rất', 'quá', 'lắm', 'hơn', 'nhất', 'cùng', 'chỉ', 'mỗi', 'mọi', 'các',
    'những', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười',
    'thứ', 'lần', 'lúc', 'khi', 'nếu', 'thì', 'vì', 'tại', 'bởi_vì',
    # Common verbs
    'làm', 'đi', 'đến', 'ra', 'vào', 'lên', 'xuống', 'biết', 'thấy', 'nghe',
    'nói', 'hỏi', 'trả_lời', 'cho', 'lấy', 'đưa', 'mang', 'đem', 'gọi',
    # Time words
    'hôm', 'nay', 'mai', 'hôm_nay', 'ngày_mai', 'hôm_qua', 'bây_giờ', 'lúc_này',
    'sau', 'trước', 'đầu', 'cuối', 'giữa',
}

# English stopwords for mixed content
EN_STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
    'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'
}

# POS tags to keep (meaningful words)
# N: Noun, Np: Proper noun, V: Verb, A: Adjective
MEANINGFUL_POS_TAGS = {'N', 'Np', 'V', 'A', 'Nc', 'Nu', 'Ny'}


class ResearchService:
    """
    Research service for text analysis
    Can use LLM API for advanced features or fallback to basic analysis
    """

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.use_llm = bool(self.openai_api_key)

    def analyze(self, text, analysis_type='summary'):
        """
        Analyze text based on type
        Types: summary, explain, keywords, questions
        """
        if analysis_type == 'keywords':
            # Always use Vietnamese keyword extraction for keywords
            return self._extract_keywords_vietnamese(text)
        
        if self.use_llm:
            return self._analyze_with_llm(text, analysis_type)
        else:
            return self._analyze_basic(text, analysis_type)

    def _analyze_basic(self, text, analysis_type):
        """Basic analysis without LLM"""
        if analysis_type == 'summary':
            return self._basic_summary(text)
        elif analysis_type == 'questions':
            return self._generate_basic_questions(text)
        else:
            return {'result': 'Analysis type not supported without LLM API'}

    def _extract_keywords_vietnamese(self, text):
        """
        Extract keyphrases from Vietnamese text using Hybrid Approach:
        1. POS tagging with underthesea
        2. Extract proper nouns (Np) - names, titles
        3. Generate meaningful n-grams (2-4 words)
        4. Combine single keywords + keyphrases
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return {
                'success': False,
                'type': 'keywords',
                'error': 'Text trống',
                'result': []
            }
        
        # Check if underthesea is available
        if not UNDERTHESEA_AVAILABLE:
            return self._extract_keywords_fallback(text)
        
        try:
            # Step 1: POS tagging
            pos_results = pos_tag(text)
            
            all_keyphrases = []
            
            # Step 2: Extract proper nouns (Np) - likely names/titles
            # These are already multi-word if detected as proper noun
            proper_nouns = []
            for word, tag in pos_results:
                if tag == 'Np' and len(word) >= 2:
                    word_clean = word.strip()
                    if word_clean and word_clean.lower() not in VN_STOPWORDS:
                        proper_nouns.append({
                            'keyword': word_clean,
                            'type': 'proper_noun',
                            'pos': 'Np'
                        })
            
            # Step 3: Generate n-grams from POS results
            # Only keep n-grams that contain meaningful words (N, V, A, Np)
            ngram_keyphrases = self._extract_meaningful_ngrams(pos_results)
            
            # Step 4: Extract single meaningful words (as backup)
            single_keywords = []
            for word, tag in pos_results:
                word_lower = word.lower().strip()
                if len(word_lower) >= 2 and tag in MEANINGFUL_POS_TAGS:
                    if word_lower not in VN_STOPWORDS and word_lower not in EN_STOPWORDS:
                        single_keywords.append({
                            'keyword': word,
                            'type': 'single',
                            'pos': tag
                        })
            
            # Step 5: Combine and deduplicate
            # Priority: Proper nouns > N-grams > Single words
            seen_lower = set()
            
            # Add proper nouns first (highest priority)
            for pn in proper_nouns:
                key = pn['keyword'].lower()
                if key not in seen_lower:
                    seen_lower.add(key)
                    all_keyphrases.append(pn)
            
            # Add n-grams
            for ng in ngram_keyphrases:
                key = ng['keyword'].lower()
                # Skip if this n-gram is contained in or contains existing keyphrases
                is_duplicate = False
                for seen in seen_lower:
                    if key in seen or seen in key:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    seen_lower.add(key)
                    all_keyphrases.append(ng)
            
            # Add single keywords if we need more
            if len(all_keyphrases) < 10:
                for sk in single_keywords:
                    key = sk['keyword'].lower()
                    # Only add if not part of existing keyphrases
                    is_contained = any(key in seen for seen in seen_lower)
                    if not is_contained and key not in seen_lower:
                        seen_lower.add(key)
                        all_keyphrases.append(sk)
                        if len(all_keyphrases) >= 12:
                            break
            
            # Step 6: Count frequency and score
            text_lower = text.lower()
            for kp in all_keyphrases:
                keyword = kp['keyword']
                # Count occurrences in original text
                count = text_lower.count(keyword.lower())
                kp['count'] = max(count, 1)
                
                # Score: prioritize proper nouns and longer phrases
                base_score = count / len(text.split()) if text.split() else 0
                length_bonus = len(keyword.split()) * 0.2  # Bonus for multi-word
                type_bonus = 0.3 if kp['type'] == 'proper_noun' else (0.2 if kp['type'] == 'ngram' else 0)
                kp['score'] = round(base_score + length_bonus + type_bonus, 4)
            
            # Step 7: Sort by score and limit
            all_keyphrases.sort(key=lambda x: x['score'], reverse=True)
            top_keyphrases = all_keyphrases[:10]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                'success': True,
                'type': 'keywords',
                'result': top_keyphrases,
                'keywords_simple': [k['keyword'] for k in top_keyphrases],
                'processing_time_ms': processing_time,
                'method': 'hybrid_keyphrase'
            }
            
        except Exception as e:
            # Fallback to basic extraction
            return self._extract_keywords_fallback(text)
    
    def _extract_meaningful_ngrams(self, pos_results, max_n=4):
        """
        Extract meaningful n-grams (2 to max_n words) from POS-tagged results.
        Only keep n-grams that contain at least one meaningful word (N, V, A, Np).
        """
        ngrams = []
        words_tags = [(w, t) for w, t in pos_results]
        
        for n in range(2, max_n + 1):
            for i in range(len(words_tags) - n + 1):
                window = words_tags[i:i+n]
                words = [w for w, t in window]
                tags = [t for w, t in window]
                
                # Check if n-gram has at least one meaningful word
                has_meaningful = any(t in MEANINGFUL_POS_TAGS for t in tags)
                if not has_meaningful:
                    continue
                
                # Skip if starts or ends with stopword
                first_word = words[0].lower()
                last_word = words[-1].lower()
                if first_word in VN_STOPWORDS or last_word in VN_STOPWORDS:
                    continue
                
                # Skip if all words are stopwords
                non_stop = [w for w in words if w.lower() not in VN_STOPWORDS]
                if len(non_stop) < 2:
                    continue
                
                # Create keyphrase
                keyphrase = ' '.join(words)
                
                # Skip very short keyphrases
                if len(keyphrase) < 4:
                    continue
                
                # Determine dominant POS
                pos_counts = Counter(tags)
                dominant_pos = pos_counts.most_common(1)[0][0]
                
                ngrams.append({
                    'keyword': keyphrase,
                    'type': 'ngram',
                    'pos': dominant_pos,
                    'length': n
                })
        
        # Deduplicate similar n-grams (prefer longer ones)
        ngrams.sort(key=lambda x: x['length'], reverse=True)
        unique_ngrams = []
        seen_parts = set()
        
        for ng in ngrams:
            key = ng['keyword'].lower()
            # Check if this is a substring of existing longer n-gram
            is_substring = any(key in seen for seen in seen_parts)
            if not is_substring:
                seen_parts.add(key)
                unique_ngrams.append(ng)
        
        return unique_ngrams
    
    def _extract_keywords_fallback(self, text):
        """Fallback keyword extraction when underthesea is not available"""
        start_time = time.time()
        
        # Simple regex-based extraction for Vietnamese
        # Match Vietnamese words (including diacritics)
        pattern = r'\b[a-zA-ZÀ-ỹ]{2,}\b'
        words = re.findall(pattern, text.lower())
        
        # Filter stopwords
        all_stopwords = VN_STOPWORDS | EN_STOPWORDS
        filtered_words = [w for w in words if w not in all_stopwords]
        
        # Count and rank
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(10)
        
        keywords_with_scores = [
            {
                'keyword': word,
                'score': round(count / len(filtered_words) if filtered_words else 0, 4),
                'count': count,
                'pos': 'unknown'
            }
            for word, count in top_words
        ]
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'type': 'keywords',
            'result': keywords_with_scores,
            'keywords_simple': [k['keyword'] for k in keywords_with_scores],
            'processing_time_ms': processing_time,
            'method': 'fallback_regex'
        }

    def _basic_summary(self, text):
        """Create basic summary (first few sentences)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Take first 3 sentences as summary
        summary = '. '.join(sentences[:3])
        if summary and not summary.endswith('.'):
            summary += '.'

        return {
            'success': True,
            'type': 'summary',
            'result': summary if summary else 'Text too short to summarize.'
        }

    def _generate_basic_questions(self, text):
        """Generate basic review questions"""
        keywords_result = self._extract_keywords_vietnamese(text)
        keywords = keywords_result.get('keywords_simple', [])[:5]

        questions = []
        for kw in keywords:
            questions.append(f"'{kw}' trong văn bản này có ý nghĩa gì?")

        if not questions:
            questions = ["Chủ đề chính của văn bản này là gì?"]

        return {
            'success': True,
            'type': 'questions',
            'result': questions
        }

    def _analyze_with_llm(self, text, analysis_type):
        """Analyze using OpenAI API"""
        try:
            import openai
            openai.api_key = self.openai_api_key

            prompts = {
                'summary': f"Summarize the following text concisely:\n\n{text}",
                'explain': f"Explain the following text in simple terms:\n\n{text}",
                'keywords': f"Extract the main keywords and concepts from:\n\n{text}",
                'questions': f"Generate 5 review questions based on:\n\n{text}"
            }

            prompt = prompts.get(analysis_type, prompts['summary'])

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )

            return {
                'success': True,
                'type': analysis_type,
                'result': response.choices[0].message.content
            }
        except Exception as e:
            # Fallback to basic analysis
            return self._analyze_basic(text, analysis_type)
