
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import torch
import sentencepiece

print("a")
MODEL_PATH = r"D:\\bartPho\\bartpho_correction_model"

print("🔄 Loading BART model... (only once)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

print("✅ BART model loaded on:", device)


def preprocess_for_model(text: str):
    text = text.lower()
    text = re.sub(r"[^0-9a-zA-ZÀ-ỹ\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def run_bart_model(text: str) -> str:
    text = preprocess_for_model(text)

    inputs = tokenizer(text, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_length=256,
            num_beams=5,
            early_stopping=True
        )

    result = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return result
