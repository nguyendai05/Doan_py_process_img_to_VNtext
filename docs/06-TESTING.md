# 🧪 Testing

## Test Files

| File | Loại | Mô tả |
|------|------|-------|
| `test_tts_api_endpoint.py` | Unit Test | Tests cho TTS API endpoint |
| `test_tts_cache_roundtrip_property.py` | Property Test | Cache round-trip consistency |
| `test_tts_hash_property.py` | Property Test | Hash consistency |
| `test_tts_invalid_input_property.py` | Property Test | Invalid input rejection |
| `test_translate_api_endpoint.py` | Unit Test | Tests cho Translate API endpoint |
| `test_translation_cache_roundtrip_property.py` | Property Test | Cache round-trip consistency |
| `test_translation_hash_property.py` | Property Test | Hash consistency |
| `test_translation_invalid_input_property.py` | Property Test | Invalid input rejection |

## Chạy Tests

### Chạy tất cả tests
```bash
pytest tests/ -v
```

### Chạy specific test file
```bash
pytest tests/test_tts_api_endpoint.py -v
```

### Chạy với coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Chạy property tests với nhiều iterations
```bash
pytest tests/test_tts_hash_property.py -v --hypothesis-seed=0
```

---

## Unit Tests

### TTS API Endpoint Tests

| Test | Mô tả | Requirements |
|------|-------|--------------|
| `test_successful_tts_generation` | TTS thành công với text và language hợp lệ | 1.3 |
| `test_cache_hit_scenario` | Request thứ 2 trả về cached audio | 3.2 |
| `test_empty_text_error` | Error khi text rỗng | 5.2 |
| `test_whitespace_only_text_error` | Error khi text chỉ có whitespace | 5.2 |
| `test_text_too_long_error` | Error khi text > 2000 chars | 5.3 |
| `test_unsupported_language_error` | Error khi language không hỗ trợ | 1.3 |
| `test_missing_text_field_error` | Error khi thiếu field text | 5.2 |
| `test_default_language_when_not_provided` | Default language 'vi' | 1.3 |

### Translate API Endpoint Tests

| Test | Mô tả | Requirements |
|------|-------|--------------|
| `test_successful_translation` | Translation thành công | 2.3 |
| `test_cache_hit_scenario` | Request thứ 2 trả về cached translation | 3.2 |
| `test_empty_text_error` | Error khi text rỗng | 5.2 |
| `test_whitespace_only_text_error` | Error khi text chỉ có whitespace | 5.2 |
| `test_text_too_long_error` | Error khi text > 2000 chars | 5.3 |
| `test_same_language_error` | Error khi source = dest language | 1.5 |
| `test_same_language_allowed_with_auto_detect` | Cho phép khi source = 'auto' | 1.5 |
| `test_missing_text_field_error` | Error khi thiếu field text | 5.2 |
| `test_default_languages_when_not_provided` | Default dest='en', src='auto' | 2.3 |

---

## Property-based Tests

Sử dụng `hypothesis` library để test với random inputs.

### Hash Consistency Tests

**Mục đích:** Đảm bảo hash function luôn trả về kết quả nhất quán.

```python
@given(text=st.text(min_size=1, max_size=1000),
       language=st.sampled_from(['vi', 'en', 'fr']))
def test_hash_consistency(text, language):
    hash1 = TTSCacheService.get_cache_key(text, language)
    hash2 = TTSCacheService.get_cache_key(text, language)
    assert hash1 == hash2
```

**Properties tested:**
- Same input → Same hash
- Different input → Different hash (với xác suất cao)
- Hash length = 64 (SHA256 hex)

### Cache Round-trip Tests

**Mục đích:** Đảm bảo data được lưu và đọc từ cache chính xác.

```python
@given(text=st.text(min_size=1, max_size=500),
       language=st.sampled_from(['vi', 'en']))
def test_cache_roundtrip(text, language):
    # Save to cache
    save_to_cache(text, language, file_path, user_id)
    
    # Read from cache
    cached = find_cached(text, language)
    
    assert cached is not None
    assert cached.text_content == text
    assert cached.language == language
```

**Properties tested:**
- Saved data = Retrieved data
- Cache hit after save
- No data corruption

### Invalid Input Rejection Tests

**Mục đích:** Đảm bảo API reject invalid inputs đúng cách.

```python
@given(text=st.text(min_size=2001, max_size=3000))
def test_reject_long_text(text):
    response = client.post('/api/tools/tts', json={'text': text})
    assert response.status_code == 400
    assert response.json['error_code'] == 'TEXT_TOO_LONG'
```

**Properties tested:**
- Empty text → EMPTY_TEXT error
- Whitespace-only text → EMPTY_TEXT error
- Text > 2000 chars → TEXT_TOO_LONG error
- Invalid language → UNSUPPORTED_LANGUAGE error

---

## Test Configuration

### TestConfig class

```python
class TestConfig:
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    TTS_OUTPUT_FOLDER = None  # Set to temp dir
    OCR_LANGUAGES = ['en', 'vi']
    MAX_TEXT_LENGTH = 2000
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
```

### Fixtures

```python
@pytest.fixture
def app_context():
    """Create app context with temp directory"""
    temp_dir = tempfile.mkdtemp()
    TestConfig.TTS_OUTPUT_FOLDER = temp_dir
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(email='test@test.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        yield app, user
        
        db.session.remove()
        db.drop_all()
    
    shutil.rmtree(temp_dir, ignore_errors=True)
```

---

## Mocking

### Mock gTTS

```python
with patch('app.services.tts_service.gTTS') as mock_gtts:
    mock_tts_instance = MagicMock()
    mock_gtts.return_value = mock_tts_instance
    
    def mock_save(filepath):
        with open(filepath, 'wb') as f:
            f.write(b'fake audio content')
    mock_tts_instance.save.side_effect = mock_save
```

### Mock Translator

```python
with patch('app.services.translate_service.Translator') as mock_translator_class:
    mock_translator = MagicMock()
    mock_translator_class.return_value = mock_translator
    
    mock_result = MagicMock()
    mock_result.text = 'Xin chào thế giới'
    mock_result.src = 'en'
    mock_translator.translate.return_value = mock_result
```

---

*Xem thêm: [07-INSTALLATION.md](07-INSTALLATION.md) - Hướng dẫn cài đặt*
