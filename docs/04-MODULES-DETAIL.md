# 📚 Chi Tiết Kỹ Thuật - 4 Module Chính

Tài liệu mô tả chi tiết chức năng, cách thức hoạt động, và thư viện sử dụng của các module:
1. [Giải thích thuật ngữ](#-giải-thích-thuật-ngữ-chuyên-ngành)
2. [Authentication](#1-authentication-module)
3. [Keyword Extraction (Research)](#2-keyword-extraction-module)
4. [BART Correction](#3-bart-correction-module)
5. [TTS Service](#4-tts-service)

---

## 📖 Giải thích Thuật ngữ Chuyên ngành

> **Mục đích**: Giúp người đọc hiểu các thuật ngữ tiếng Anh chuyên ngành được sử dụng trong tài liệu.

### 🔐 Authentication (Xác thực)

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **Authentication** | /ɔːˌθentɪˈkeɪʃn/ | **Xác thực** - Quá trình kiểm tra danh tính người dùng (bạn là ai?). VD: đăng nhập bằng email + password. |
| **Session** | /ˈseʃn/ | **Phiên làm việc** - Khoảng thời gian từ lúc đăng nhập đến khi đăng xuất. Server ghi nhớ bạn đã đăng nhập. |
| **Hash** | /hæʃ/ | **Băm** - Biến đổi dữ liệu thành chuỗi ký tự cố định. Giống như "nghiền nhỏ" password thành mã không thể đảo ngược. VD: "abc123" → "$2b$12$xxxxx" |
| **Salt** | /sɔːlt/ | **Muối** - Chuỗi ngẫu nhiên thêm vào password trước khi hash. Giống như thêm "gia vị" để 2 người cùng password có hash khác nhau. |
| **bcrypt** | /biːˈkrɪpt/ | Thuật toán hash password phổ biến, chậm có chủ đích để chống hack. |
| **One-way hash** | - | **Hash một chiều** - Chỉ có thể biến password → hash, không thể hash → password. Như "không thể nấu ngược bột thành gạo". |
| **Brute-force attack** | /bruːt fɔːs/ | **Tấn công thử tất cả** - Hacker thử hàng triệu password để đoán đúng. bcrypt chậm để chống lại. |
| **Rainbow table attack** | - | Hacker dùng bảng tra hash sẵn. Salt chống lại bằng cách mỗi hash là duy nhất. |
| **ORM** | - | **Object-Relational Mapping** - Công cụ giúp code Python làm việc với database dễ hơn. Thay vì viết SQL, viết code Python. |
| **Primary Key** | - | **Khóa chính** - Cột định danh duy nhất mỗi hàng trong bảng. VD: `id = 1, 2, 3...` |
| **Foreign Key (FK)** | - | **Khóa ngoại** - Cột liên kết với bảng khác. VD: `user_id` trong bảng `tts_audio` trỏ về bảng `users`. |
| **Index** | /ˈɪndeks/ | **Chỉ mục** - Cấu trúc giúp tìm kiếm nhanh hơn trong database. Giống mục lục sách. |
| **API Endpoint** | - | **Điểm cuối API** - Địa chỉ URL mà client gọi tới. VD: `/api/auth/login` |
| **Blueprint** | /ˈbluːprɪnt/ | Flask Blueprint - Cách tổ chức code thành các module riêng biệt. |

### 🔤 NLP - Xử lý Ngôn ngữ Tự nhiên

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **NLP** | - | **Natural Language Processing** - Xử lý ngôn ngữ tự nhiên. Dạy máy tính hiểu tiếng người. |
| **Tokenize** | /ˈtəʊkənaɪz/ | **Tách từ** - Chia câu thành các từ riêng lẻ. VD: "Tôi yêu Việt Nam" → ["Tôi", "yêu", "Việt_Nam"] |
| **Token** | /ˈtəʊkən/ | **Đơn vị từ** - Một từ hoặc ký hiệu sau khi tách. |
| **POS Tagging** | - | **Part-of-Speech Tagging** - Gán nhãn từ loại. VD: "chạy" → Verb, "xe" → Noun |
| **POS Tags** | - | Các nhãn từ loại: **N** (Noun=Danh từ), **V** (Verb=Động từ), **A** (Adjective=Tính từ), **Np** (Proper Noun=Danh từ riêng) |
| **N-gram** | /ˈen ɡræm/ | **Cụm n từ liên tiếp** - VD: bigram (2 từ): "trí tuệ", trigram (3 từ): "trí tuệ nhân" |
| **Keyphrase** | /ˈkiːfreɪz/ | **Cụm từ khóa** - Các từ/cụm từ quan trọng đại diện cho nội dung văn bản. |
| **Stopword** | /ˈstɒpwɜːd/ | **Từ dừng** - Những từ không mang ý nghĩa như: và, hoặc, của, là, được... Cần loại bỏ khi phân tích. |
| **Proper Noun** | - | **Danh từ riêng** - Tên người, địa danh, tổ chức. VD: "Việt Nam", "Microsoft" |
| **Frequency** | /ˈfriːkwənsi/ | **Tần suất** - Số lần xuất hiện của từ trong văn bản. |
| **Score** | /skɔː/ | **Điểm số** - Mức độ quan trọng của từ khóa (0.0 đến 1.0). |
| **underthesea** | - | Thư viện NLP tiếng Việt nguồn mở. Hỗ trợ tokenize, POS tag, NER cho tiếng Việt. |

### 🤖 AI/Deep Learning (BART Module)

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **BART** | /bɑːt/ | **Bidirectional and Auto-Regressive Transformers** - Mô hình AI của Facebook, giỏi sửa lỗi văn bản. |
| **BARTpho** | - | BART được huấn luyện riêng cho tiếng Việt. "pho" = tiếng Việt 🍲 |
| **Transformer** | /trænsˈfɔːmə/ | Kiến trúc AI hiện đại (2017), nền tảng của GPT, BERT, BART. Hiểu ngữ cảnh tốt hơn. |
| **Pre-trained Model** | - | **Mô hình đã huấn luyện sẵn** - Model được train trên dữ liệu lớn, chỉ cần fine-tune cho task cụ thể. |
| **Fine-tune** | /faɪn tjuːn/ | **Tinh chỉnh** - Huấn luyện thêm model sẵn có cho nhiệm vụ cụ thể (sửa lỗi OCR). |
| **Seq2Seq** | - | **Sequence-to-Sequence** - Model nhận chuỗi đầu vào, tạo chuỗi đầu ra. VD: "xin cào" → "xin chào" |
| **Tokenizer** | - | Công cụ chuyển text thành số (tokens) để model hiểu. |
| **Inference** | /ˈɪnfərəns/ | **Suy luận** - Quá trình model đưa ra kết quả từ dữ liệu mới (không phải training). |
| **Tensor** | /ˈtensə/ | Mảng đa chiều chứa số. Dữ liệu trong AI được biểu diễn bằng tensor. |
| **GPU** | - | **Graphics Processing Unit** - Card đồ họa. Xử lý AI nhanh hơn CPU 10-100 lần. |
| **CUDA** | /ˈkuːdə/ | Công nghệ NVIDIA cho phép dùng GPU chạy AI. |
| **CPU Fallback** | - | Khi không có GPU, chương trình tự chuyển sang dùng CPU (chậm hơn). |
| **Beam Search** | - | Thuật toán tìm kiếm kết quả tốt nhất. `num_beams=4` = thử 4 "nhánh" cùng lúc rồi chọn tốt nhất. |
| **max_length** | - | Số token tối đa model xuất ra. VD: 256 tokens ≈ 100-150 từ tiếng Việt. |
| **Chunk** | /tʃʌŋk/ | **Mảnh/Khối** - Chia text dài thành nhiều phần nhỏ (~200 ký tự) để xử lý. |
| **PyTorch** | /ˈpaɪ tɔːtʃ/ | Framework deep learning phổ biến của Facebook. |
| **Hugging Face** | /ˈhʌɡɪŋ feɪs/ | Công ty/Platform chia sẻ model AI. Thư viện `transformers` của họ. |
| **SentencePiece** | - | Thuật toán tokenize của Google. Chia câu thành "subwords" (từ con). |
| **safetensors** | - | Format lưu model weights an toàn, nhanh hơn pickle. |

### 🔊 TTS - Text-to-Speech

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **TTS** | - | **Text-to-Speech** - Chuyển văn bản thành giọng nói. Máy tính "đọc" văn bản. |
| **gTTS** | - | **Google Text-to-Speech** - Thư viện Python gọi API Google để tạo giọng nói. |
| **Cache** | /kæʃ/ | **Bộ nhớ đệm** - Lưu trữ kết quả để dùng lại, tránh tính toán lặp lại. |
| **Cache Hit** | - | Tìm thấy trong cache → trả về ngay, không cần tạo mới. |
| **Cache Miss** | - | Không có trong cache → phải tạo mới rồi lưu. |
| **Stale Cache** | - | **Cache lỗi thời** - File audio bị xóa nhưng record DB còn. Cần xóa record và tạo lại. |
| **SHA256** | - | Thuật toán hash tạo mã 64 ký tự duy nhất từ dữ liệu. Dùng làm cache key. |
| **UUID** | - | **Universally Unique Identifier** - Mã định danh duy nhất toàn cầu. VD: `a1b2c3d4-e5f6-...` |
| **MP3** | - | Format file âm thanh nén phổ biến. |

### 🗄️ Database

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **Schema** | /ˈskiːmə/ | **Lược đồ** - Cấu trúc bảng: tên cột, kiểu dữ liệu, ràng buộc. |
| **VARCHAR** | - | **Variable Character** - Kiểu chuỗi ký tự có độ dài thay đổi. VD: VARCHAR(255) = tối đa 255 ký tự. |
| **TEXT** | - | Kiểu chuỗi không giới hạn độ dài (cho nội dung dài). |
| **INTEGER** | - | Kiểu số nguyên: 1, 2, 3, -5... |
| **BOOLEAN** | - | Kiểu true/false (đúng/sai). |
| **DATETIME** | - | Kiểu ngày giờ: 2026-01-25 13:45:00 |
| **nullable** | - | Cho phép giá trị NULL (trống). |
| **unique** | - | Giá trị phải duy nhất, không trùng lặp. |
| **auto increment** | - | Tự động tăng: 1, 2, 3... khi thêm record mới. |

### 🌐 Web/API

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **API** | - | **Application Programming Interface** - Giao diện để các phần mềm giao tiếp nhau. |
| **REST API** | - | Kiểu API phổ biến dùng HTTP methods (GET, POST, PUT, DELETE). |
| **JSON** | /ˈdʒeɪsən/ | **JavaScript Object Notation** - Format dữ liệu nhẹ. VD: `{"name": "Hà Nội", "code": "HN"}` |
| **Request** | /rɪˈkwest/ | **Yêu cầu** - Client gửi đến server. |
| **Response** | /rɪˈspɒns/ | **Phản hồi** - Server trả về cho client. |
| **Client** | /ˈklaɪənt/ | **Máy khách** - Trình duyệt, app di động, bất kỳ ai gọi API. |
| **Server** | /ˈsɜːvə/ | **Máy chủ** - Nơi xử lý logic, lưu dữ liệu. |
| **Static file** | - | File tĩnh (hình ảnh, CSS, JS, audio) không thay đổi. Truy cập trực tiếp qua URL. |

### 📷 OCR

| Thuật ngữ | Phiên âm | Giải thích tiếng Việt |
|-----------|----------|----------------------|
| **OCR** | - | **Optical Character Recognition** - Nhận dạng ký tự quang học. "Đọc" chữ từ hình ảnh. |
| **EasyOCR** | - | Thư viện OCR hỗ trợ 80+ ngôn ngữ, bao gồm tiếng Việt. |
| **Preprocessing** | - | **Tiền xử lý** - Chỉnh sửa ảnh (grayscale, denoise...) trước khi OCR để tăng độ chính xác. |
| **Segment** | /ˈseɡmənt/ | **Đoạn** - Một vùng text được OCR nhận diện, có tọa độ và độ tin cậy. |
| **Confidence** | /ˈkɒnfɪdəns/ | **Độ tin cậy** - Mức độ chắc chắn của OCR (0.0 - 1.0). VD: 0.95 = 95% chắc chắn. |
| **Bounding Box (bbox)** | - | Hình chữ nhật bao quanh vùng text được phát hiện. |

---

## 1. Authentication Module

### 📁 Files liên quan
- `app/routes/auth.py` - API endpoints xác thực
- `app/models/user.py` - User model và password hashing

### 🎯 Chức năng
Module quản lý việc đăng ký, đăng nhập, đăng xuất và phiên làm việc của người dùng.

### 🛠️ Thư viện sử dụng

| Thư viện | Phiên bản | Chức năng |
|----------|-----------|-----------|
| **Flask-Login** | - | Quản lý session người dùng, login/logout |
| **bcrypt** | - | Mã hóa mật khẩu một chiều (one-way hash) |
| **Flask-SQLAlchemy** | - | ORM kết nối database |

### 🔄 Cách thức hoạt động

#### 1. Đăng ký (Register)
```
[Client] --POST /api/auth/register--> [Server]
                                        │
                                        ├── 1. Validate: email không trống, password >= 6 ký tự
                                        ├── 2. Check email unique trong database
                                        ├── 3. Hash password bằng bcrypt + salt tự động
                                        ├── 4. Tạo User record, lưu vào database
                                        └── 5. Trả về thông tin user (không kèm password)
```

**Chi tiết Hash Password (bcrypt):**
```python
# Tạo salt ngẫu nhiên và hash password
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),   # Encode password thành bytes
    bcrypt.gensalt()            # Tự động tạo salt 22 ký tự
)
# Output: $2b$12$xxxxx... (60 ký tự)
```

#### 2. Đăng nhập (Login)
```
[Client] --POST /api/auth/login--> [Server]
                                      │
                                      ├── 1. Tìm user theo email
                                      ├── 2. So sánh password với hash trong DB
                                      │       └── bcrypt.checkpw(password, hash)
                                      ├── 3. Kiểm tra user.is_active == True
                                      ├── 4. Cập nhật last_login_at
                                      ├── 5. Tạo session (Flask-Login)
                                      └── 6. Trả về user info
```

#### 3. Kiểm tra Session
```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Flask-Login tự động gọi hàm này mỗi request để load user từ session
```

### 📊 Database Schema

| Column | Type | Mô tả |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto increment |
| `email` | VARCHAR(255) | Email unique, có index |
| `password_hash` | VARCHAR(255) | bcrypt hash (~60 chars) |
| `full_name` | VARCHAR(100) | Tên hiển thị (nullable) |
| `avatar_url` | VARCHAR(500) | URL avatar (nullable) |
| `is_active` | BOOLEAN | Trạng thái tài khoản |
| `last_login_at` | DATETIME | Thời điểm đăng nhập gần nhất |
| `created_at` | DATETIME | Thời điểm tạo |
| `updated_at` | DATETIME | Thời điểm cập nhật |

### 🔒 Bảo mật
- **bcrypt**: Sử dụng thuật toán Blowfish, cost factor 12 (mặc định), chống brute-force
- **Salt tự động**: Mỗi password có salt riêng, chống rainbow table attack
- **Session-based**: Không lưu password trong cookie, chỉ session ID

---

## 2. Keyword Extraction Module

### 📁 Files liên quan
- `app/services/research_service.py` - Service trích xuất từ khóa

### 🎯 Chức năng
Trích xuất **keyphrases** (cụm từ khóa có nghĩa) từ văn bản tiếng Việt sử dụng phương pháp **Hybrid** kết hợp:
- POS Tagging (Gán nhãn từ loại)
- N-gram extraction (Trích xuất cụm từ)
- Proper noun detection (Phát hiện danh từ riêng)

### 🛠️ Thư viện sử dụng

| Thư viện | Chức năng |
|----------|-----------|
| **underthesea** | NLP tiếng Việt: word_tokenize, pos_tag |
| **collections.Counter** | Đếm tần suất từ |
| **re (regex)** | Pattern matching cho fallback |

### 🔄 Cách thức hoạt động

#### Quy trình Hybrid Keyphrase Extraction

```
[Input Text] 
     │
     ▼
┌─────────────────────────────────────┐
│ Step 1: POS Tagging (underthesea)   │
│   pos_tag(text) → [(word, tag), ...]│
│   VD: [("Việt_Nam", "Np"),          │
│        ("phát_triển", "V"), ...]    │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Step 2: Extract Proper Nouns (Np)   │
│   - Lọc các token có tag = "Np"     │
│   - VD: "Việt_Nam", "Hà_Nội"        │
│   - Đây thường là tên riêng quan trọng│
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Step 3: Generate Meaningful N-grams │
│   - N = 2 đến 4 từ                  │
│   - Chỉ giữ n-gram chứa từ có nghĩa │
│     (N: Noun, V: Verb, A: Adjective)│
│   - Bỏ n-gram bắt đầu/kết thúc      │
│     bằng stopword                   │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Step 4: Extract Single Keywords    │
│   - Backup: từ đơn có nghĩa         │
│   - Filter stopwords VN + EN        │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Step 5: Combine & Deduplicate      │
│   Priority: Proper Nouns > N-grams  │
│             > Single Keywords       │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Step 6: Score & Rank               │
│   score = frequency + length_bonus  │
│         + type_bonus                │
│   - Proper noun: +0.3               │
│   - N-gram: +0.2                    │
│   - Multi-word: +0.2 × word_count   │
└─────────────────────────────────────┘
     │
     ▼
[Top 10 Keyphrases Output]
```

#### POS Tags được giữ lại (Meaningful)

| Tag | Ý nghĩa | Ví dụ |
|-----|---------|-------|
| **N** | Danh từ (Noun) | "công nghệ", "phần mềm" |
| **Np** | Danh từ riêng (Proper noun) | "Việt Nam", "Microsoft" |
| **V** | Động từ (Verb) | "phát triển", "sử dụng" |
| **A** | Tính từ (Adjective) | "mới", "hiện đại" |
| **Nc** | Danh từ chỉ loại | "chiếc", "cái" |
| **Nu** | Danh từ đơn vị | "mét", "kg" |
| **Ny** | Danh từ viết tắt | "AI", "ML" |

#### Vietnamese Stopwords (Loại bỏ)

Danh sách ~100 stopwords tiếng Việt bao gồm:
- Đại từ: tôi, bạn, anh, chị, họ, nó...
- Liên từ: và, hoặc, nhưng, mà, vì...
- Giới từ: trong, ngoài, trên, dưới, từ, đến...
- Trợ động từ: sẽ, đã, đang, được, bị...
- Từ chỉ thời gian: hôm, nay, mai, ngày...

### 📤 Output Format

```json
{
  "success": true,
  "type": "keywords",
  "result": [
    {
      "keyword": "trí tuệ nhân tạo",
      "type": "ngram",
      "pos": "N",
      "count": 5,
      "score": 0.45
    },
    {
      "keyword": "Việt Nam",
      "type": "proper_noun", 
      "pos": "Np",
      "count": 3,
      "score": 0.38
    }
  ],
  "keywords_simple": ["trí tuệ nhân tạo", "Việt Nam", ...],
  "processing_time_ms": 125,
  "method": "hybrid_keyphrase"
}
```

### 🔄 Fallback Mode

Khi **underthesea** không khả dụng:
```
[Input] → Regex tokenize → Filter stopwords → Count frequency → Top 10
```
- Sử dụng regex: `\b[a-zA-ZÀ-ỹ]{2,}\b`
- Method: `"fallback_regex"`

---

## 3. BART Correction Module

### 📁 Files liên quan
- `app/services/model_inference.py` - Load và inference BART model
- `app/services/summarize_service.py` - Tóm tắt văn bản (dùng chung NLP)

### 🎯 Chức năng
Sửa lỗi OCR tiếng Việt sử dụng model **BARTpho** (BART pre-trained cho tiếng Việt) đã được fine-tune cho task sửa lỗi chính tả.

### 🛠️ Thư viện sử dụng

| Thư viện | Phiên bản | Chức năng |
|----------|-----------|-----------|
| **transformers** | - | Hugging Face library, load pretrained models |
| **torch (PyTorch)** | - | Deep learning framework, tensor operations |
| **sentencepiece** | - | Tokenization cho BARTpho |
| **AutoTokenizer** | - | Tự động load tokenizer phù hợp với model |
| **AutoModelForSeq2SeqLM** | - | Load BART model dạng Seq2Seq |

### 📂 Model Structure

```
models/bartpho_correction_model/
├── config.json               # Cấu hình model (architecture, vocab size...)
├── model.safetensors         # Weights đã train (~500MB)
├── tokenizer_config.json     # Cấu hình tokenizer
├── sentencepiece.bpe.model   # BPE vocabulary
├── special_tokens_map.json   # Special tokens (<s>, </s>, <pad>...)
└── generation_config.json    # Cấu hình generate
```

### 🔄 Cách thức hoạt động

#### Quy trình Inference

```
[Raw OCR Text]
     │
     ▼
┌────────────────────────────────────┐
│ Step 1: Preprocessing              │
│   - Chuẩn hóa whitespace           │
│   - re.sub(r"\s+", " ", text)      │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ Step 2: Split into Sentences       │
│   - Tách theo: . ! ? \n            │
│   - Pattern: (?<=[.!?\n])\s+       │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ Step 3: Group into Chunks          │
│   - Gộp câu thành chunk ~200 chars │
│   - Đảm bảo không cắt giữa câu     │
│   - Lý do: BART max_length=256     │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ Step 4: Process Each Chunk (BART)  │
│   for each chunk:                  │
│     1. Tokenize (SentencePiece)    │
│     2. Encode → tensor             │
│     3. Model generate              │
│     4. Decode → text               │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ Step 5: Join Results               │
│   result = " ".join(corrected_chunks)│
└────────────────────────────────────┘
     │
     ▼
[Corrected Text]
```

#### BART Generate Configuration

```python
output_ids = model.generate(
    **inputs,
    max_length=256,      # Output tối đa 256 tokens
    num_beams=4,         # Beam search với 4 beams
    length_penalty=1.0,  # Không penalty độ dài
    early_stopping=True  # Dừng sớm khi tất cả beam đạt EOS
)
```

| Parameter | Value | Giải thích |
|-----------|-------|------------|
| `max_length` | 256 | Giới hạn output tokens |
| `num_beams` | 4 | Số beam trong beam search, tăng độ chính xác |
| `length_penalty` | 1.0 | Không ưu tiên câu ngắn/dài |
| `early_stopping` | True | Dừng khi đủ kết quả tốt |

### ⚙️ Cấu hình Runtime

```env
# .env file
USE_BART_MODEL=true   # Bật/tắt BART module
```

- **GPU**: Tự động detect CUDA, sử dụng GPU nếu có
- **CPU Fallback**: Chạy trên CPU nếu không có GPU
- **Lazy Loading**: Model chỉ load 1 lần khi khởi động

### 📊 Hiệu suất

| Metric | Value |
|--------|-------|
| Model size | ~500MB |
| Load time (GPU) | 3-5 giây |
| Load time (CPU) | 10-15 giây |
| Inference/chunk (GPU) | 0.1-0.3 giây |
| Inference/chunk (CPU) | 1-3 giây |

### 🛡️ Error Handling

```python
def run_bart_model(text):
    if model is None or tokenizer is None:
        return text  # Trả về text gốc nếu model chưa load
    
    try:
        # ... inference logic
    except Exception as e:
        print(f"⚠️ BART error: {e}")
        return text  # Fallback: trả về text gốc
```

---

## 4. TTS Service

### 📁 Files liên quan
- `app/services/tts_service.py` - Text-to-Speech chính
- `app/services/tts_cache_service.py` - Caching logic
- `app/models/tts_audio.py` - Database model cho cache

### 🎯 Chức năng
Chuyển đổi văn bản thành giọng nói (Text-to-Speech) với:
- Hỗ trợ nhiều ngôn ngữ
- Caching để tránh generate lặp lại
- Lưu trữ file audio MP3

### 🛠️ Thư viện sử dụng

| Thư viện | Chức năng |
|----------|-----------|
| **gTTS** (Google Text-to-Speech) | Gọi Google TTS API, generate MP3 |
| **hashlib** | Tạo SHA256 hash cho cache key |
| **uuid** | Tạo unique filename |
| **os** | File system operations |

### 🌍 Ngôn ngữ hỗ trợ

| Code | Language | Code | Language |
|------|----------|------|----------|
| `vi` | Vietnamese | `ko` | Korean |
| `en` | English | `zh-CN` | Chinese (Simplified) |
| `fr` | French | `ja` | Japanese |
| `de` | German | `es` | Spanish |

### 🔄 Cách thức hoạt động

#### Quy trình TTS với Cache

```
[Request: text + language + user_id]
           │
           ▼
┌─────────────────────────────────────┐
│ Step 1: Generate Cache Key          │
│   key = SHA256(text + ":" + lang)   │
│   VD: SHA256("Xin chào:vi")         │
│       → "a1b2c3d4e5..."             │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 2: Check Database Cache        │
│   SELECT * FROM tts_audio           │
│   WHERE text_hash = key             │
│     AND language = lang             │
└─────────────────────────────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
[Cache Hit]  [Cache Miss]
     │           │
     ▼           ▼
┌─────────┐  ┌─────────────────────────┐
│ Verify  │  │ Step 3: Generate Audio  │
│ file    │  │   gTTS(text, lang=lang) │
│ exists  │  │   tts.save(filepath)    │
└─────────┘  └─────────────────────────┘
     │           │
     ▼           ▼
[Return URL]  ┌─────────────────────────┐
              │ Step 4: Save to Cache   │
              │   - Insert DB record    │
              │   - Store file size     │
              └─────────────────────────┘
                     │
                     ▼
               [Return URL]
```

#### Cache Key Generation

```python
def get_cache_key(text: str, language: str) -> str:
    combined = f"{text}:{language}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

# Ví dụ:
# get_cache_key("Xin chào", "vi")
# → "a1b2c3d4e5f6..."  (64 ký tự hex)
```

> **Lý do kết hợp text + language**: 
> Cùng một text với ngôn ngữ khác nhau sẽ có file audio khác nhau.
> VD: "Hello" đọc bằng `en` khác với đọc bằng `vi` (sẽ đọc theo phát âm VN)

#### File Storage

```
app/static/audio/
├── tts_a1b2c3d4.mp3
├── tts_e5f6g7h8.mp3
└── ...
```

- **Format**: MP3 (gTTS mặc định)
- **Naming**: `tts_{uuid}.mp3`
- **URL**: `/static/audio/tts_xxx.mp3`

### 📊 Database Schema (tts_audio)

| Column | Type | Mô tả |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | FK → users.id |
| `text_content` | TEXT | Nội dung text gốc |
| `text_hash` | VARCHAR(64) | SHA256 hash (index) |
| `language` | VARCHAR(10) | Mã ngôn ngữ |
| `file_path` | VARCHAR(500) | Path tới file MP3 |
| `file_size` | INTEGER | Kích thước file (bytes) |
| `duration_ms` | INTEGER | Thời lượng (nullable) |
| `text_block_id` | INTEGER | FK → text_blocks (nullable) |
| `created_at` | DATETIME | Thời điểm tạo |

### 📤 API Response

```json
{
  "success": true,
  "audio_url": "/static/audio/tts_a1b2c3d4.mp3",
  "from_cache": true,
  "duration_ms": null
}
```

| Field | Mô tả |
|-------|-------|
| `audio_url` | URL để client play audio |
| `from_cache` | `true` = lấy từ cache, `false` = mới generate |
| `duration_ms` | Thời lượng (chưa implement) |

### 🔄 Stale Cache Handling

```python
if os.path.exists(filepath):
    return cached_audio  # Cache valid
else:
    # File đã bị xóa → xóa record, generate lại
    db.session.delete(cached_audio)
    db.session.commit()
    # → Tiếp tục generate mới
```

### ⚡ Tối ưu Performance

1. **Cache First**: Luôn check cache trước khi gọi gTTS
2. **Hash Index**: `text_hash` có index để query nhanh
3. **File Verification**: Kiểm tra file tồn tại trước khi return
4. **Unique Filename**: UUID tránh collision

---

## 🔗 Quan hệ giữa các Module

```
┌─────────────┐     ┌──────────────────┐
│ Auth Module │────▶│ User Session     │
└─────────────┘     └──────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Request Flow  │
                    └───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ OCR Service   │   │ Research Svc  │   │ TTS Service   │
│ (EasyOCR)     │   │ (Keywords)    │   │ (gTTS)        │
└───────┬───────┘   └───────────────┘   └───────────────┘
        │
        ▼
┌───────────────┐
│ BART Correct  │
│ (BARTpho)     │
└───────────────┘
```

---

*Tài liệu được tạo: 2026-01-25*
*Dựa trên phân tích source code project Image-to-Text OCR*
