# Tài liệu Kỹ thuật: Trích xuất Từ khóa Tiếng Việt

## 1. Tổng quan

### 1.1 Mục đích
Trích xuất **cụm từ khóa (keyphrases)** từ văn bản tiếng Việt được người dùng select trong kết quả OCR, phục vụ cho tính năng **tìm kiếm** trong phần Research.

### 1.2 Chức năng chính
| Chức năng | Mô tả |
|-----------|-------|
| **Trích xuất keyphrases** | Lấy cụm từ 2-4 từ có ý nghĩa |
| **Nhận diện tên riêng** | Phát hiện tên người, địa danh, tên bài hát |
| **Ranking từ khóa** | Sắp xếp theo độ quan trọng |
| **Tìm kiếm nhanh** | Mở Google Search với từ khóa |

---

## 2. Giải pháp Kỹ thuật

### 2.1 Hybrid Keyphrase Extraction

Kết hợp 3 kỹ thuật:

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT: Văn bản OCR                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           1. POS Tagging (underthesea)                  │
│    Gán nhãn từ loại: Noun, Verb, Adjective, Np          │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐  ┌───────────┐  ┌─────────────┐
    │ Proper Noun │  │  N-gram   │  │   Single    │
    │ Detection   │  │ Generation│  │  Keywords   │
    │    (Np)     │  │  (2-4 từ) │  │   (backup)  │
    └─────────────┘  └───────────┘  └─────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│              2. Scoring & Ranking                       │
│   - Proper noun: +0.3 điểm                              │
│   - N-gram: +0.2 điểm                                   │
│   - Multi-word bonus: +0.2 × số từ                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│            OUTPUT: Top 10 Keyphrases                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Công nghệ sử dụng

| Thành phần | Công nghệ | Vai trò |
|------------|-----------|---------|
| **NLP Engine** | underthesea 6.8.4 | Tokenization, POS tagging tiếng Việt |
| **Backend** | Flask + Python | API endpoint `/api/tools/research` |
| **Frontend** | JavaScript | UI hiển thị keywords, nút tìm kiếm |

---

## 3. Cách thức Hoạt động

### 3.1 Flow xử lý

```python
# Step 1: POS Tagging
pos_results = pos_tag(text)
# Output: [('Lạ Lùng', 'N'), ('Vũ', 'Np'), ('bài hát', 'N'), ...]

# Step 2: Extract Proper Nouns (tên riêng)
proper_nouns = [w for w, tag in pos_results if tag == 'Np']
# Output: ['Vũ', 'Hà Nội', ...]

# Step 3: Generate N-grams (2-4 từ)
ngrams = extract_meaningful_ngrams(pos_results)
# Output: ['bài hát', 'Gió hát', 'nỗi nhớ', ...]

# Step 4: Combine & Score
all_keyphrases = proper_nouns + ngrams + single_keywords
# Scoring: base_score + length_bonus + type_bonus

# Step 5: Return Top 10
return sorted(all_keyphrases, key=lambda x: x['score'])[:10]
```

### 3.2 POS Tags quan trọng

| Tag | Ý nghĩa | Ví dụ |
|-----|---------|-------|
| **Np** | Proper Noun (Tên riêng) | Vũ, Hà Nội, Lạ Lùng |
| **N** | Noun (Danh từ) | bài hát, nỗi nhớ |
| **V** | Verb (Động từ) | hát, nhớ, yêu |
| **A** | Adjective (Tính từ) | đẹp, buồn, lạ |

### 3.3 Stopwords
Loại bỏ ~100 từ phổ biến không mang ý nghĩa:
- Đại từ: tôi, anh, em, họ...
- Liên từ: và, hoặc, nhưng, mà...
- Trợ từ: đã, đang, sẽ, được...

---

## 4. API Specification

### 4.1 Endpoint

```
POST /api/tools/research
Content-Type: application/json
```

### 4.2 Request

```json
{
    "text": "Lạ Lùng bài hát của Vũ...",
    "type": "keywords"
}
```

### 4.3 Response

```json
{
    "success": true,
    "type": "keywords",
    "result": [
        {
            "keyword": "Vũ",
            "type": "proper_noun",
            "pos": "Np",
            "count": 2,
            "score": 0.52
        },
        {
            "keyword": "bài hát",
            "type": "ngram",
            "pos": "N",
            "count": 1,
            "score": 0.45
        }
    ],
    "processing_time_ms": 13,
    "method": "hybrid_keyphrase"
}
```

---

## 5. Định hướng Phát triển

### 5.1 Cải tiến ngắn hạn
- [ ] Caching kết quả keywords vào database
- [ ] Thêm option tìm kiếm Wikipedia/Từ điển
- [ ] Highlight từ khóa trong văn bản gốc

### 5.2 Cải tiến dài hạn
- [ ] Sử dụng PhoBERT cho semantic keyword extraction
- [ ] Tích hợp Knowledge Graph để liên kết từ khóa
- [ ] Auto-suggest từ khóa liên quan

---

## 6. Files liên quan

| File | Vai trò |
|------|---------|
| `app/services/research_service.py` | Core keyword extraction logic |
| `app/routes/tools.py` | API endpoint |
| `app/static/js/app.js` | Frontend UI |
| `app/static/css/style.css` | Styling |
| `requirements.txt` | Dependencies (underthesea) |

---

## 7. Tài liệu tham khảo

- [underthesea - Vietnamese NLP](https://github.com/undertheseanlp/underthesea)
- [POS Tagging for Vietnamese](https://underthesea.readthedocs.io/en/latest/pos.html)
- [RAKE Algorithm](https://www.researchgate.net/publication/227988510_Automatic_Keyword_Extraction_from_Individual_Documents)
