from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import torch
import sentencepiece
import os
from dotenv import load_dotenv

load_dotenv()

# Model path - đặt trong thư mục models/ ở root project
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# MODEL_PATH = os.path.join(BASE_DIR, "models", "bartpho_correction_model")
MODEL_PATH = r""


tokenizer = None
model = None
device = None

USE_BART = os.getenv("USE_BART_MODEL", "true").lower() == "true"

if USE_BART and os.path.exists(MODEL_PATH):
    print("🔄 Loading BART model... (only once)")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print("✅ BART model loaded on:", device)
elif not USE_BART:
    print("⚠️ BART model disabled via USE_BART_MODEL=false")
else:
    print("⚠️ BART model not found at:", MODEL_PATH)


def preprocess_for_model(text: str):
    # Chỉ chuẩn hóa khoảng trắng, giữ nguyên text gốc
    return re.sub(r"\s+", " ", text).strip()


def split_into_sentences(text: str) -> list:
    """Chia text thành các câu dựa trên dấu câu"""
    # Tách theo dấu chấm, chấm hỏi, chấm than, xuống dòng
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def process_chunk(chunk: str) -> str:
    """Xử lý một chunk text qua BART"""
    inputs = tokenizer(
        chunk,
        return_tensors="pt",
        max_length=256,
        truncation=True,
        padding=True
    ).to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True
        )

    return tokenizer.decode(output_ids[0], skip_special_tokens=True)


def run_bart_model(text: str) -> str:
    if model is None or tokenizer is None:
        return text  # Return original if model not loaded

    try:
        processed_text = preprocess_for_model(text)
        print(f"📝 BART input ({len(processed_text)} chars)")

        # Chia thành các câu
        sentences = split_into_sentences(processed_text)
        
        # Gộp câu thành chunks (~200 chars mỗi chunk)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 200:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk)

        # Xử lý từng chunk
        results = []
        for i, chunk in enumerate(chunks):
            corrected = process_chunk(chunk)
            results.append(corrected)
            print(f"  Chunk {i+1}/{len(chunks)}: {len(chunk)} → {len(corrected)} chars")

        result = " ".join(results)
        print(f"📤 BART output ({len(result)} chars)")

        return result
    except Exception as e:
        print(f"⚠️ BART error: {e}")
        return text
