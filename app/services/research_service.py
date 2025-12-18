import os
import re
from collections import Counter


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
        if self.use_llm:
            return self._analyze_with_llm(text, analysis_type)
        else:
            return self._analyze_basic(text, analysis_type)

    def _analyze_basic(self, text, analysis_type):
        """Basic analysis without LLM"""
        if analysis_type == 'keywords':
            return self._extract_keywords(text)
        elif analysis_type == 'summary':
            return self._basic_summary(text)
        elif analysis_type == 'questions':
            return self._generate_basic_questions(text)
        else:
            return {'result': 'Analysis type not supported without LLM API'}

    def _extract_keywords(self, text):
        """Extract keywords from text"""
        # Remove punctuation and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'
        }

        # Filter and count
        filtered_words = [w for w in words if w not in stop_words]
        word_counts = Counter(filtered_words)

        # Get top 10 keywords
        keywords = [word for word, count in word_counts.most_common(10)]

        return {
            'success': True,
            'type': 'keywords',
            'result': keywords
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
        keywords = self._extract_keywords(text)['result'][:5]

        questions = []
        for kw in keywords:
            questions.append(f"What is the significance of '{kw}' in this text?")

        if not questions:
            questions = ["What is the main topic of this text?"]

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
