import os
import pandas as pd
import unicodedata
import re
from jiwer import wer

from app.services import (
    OCRService,
    init_ocr_reader,
    run_bart_model,
    TextProcessor,
    text_spliter,
    text_merger
)


IMAGE_DIR = r"C:\Users\HINH\Downloads\dataset\images"
TEXT_DIR = r"C:\Users\HINH\Downloads\dataset\texts"
OUTPUT_CSV = r"C:\Users\HINH\Downloads\dataset\ocr_evaluation.csv"


# =========================
# INIT OCR SINGLETON
# =========================
init_ocr_reader(['vi', 'en'])


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


records = []
index = 1
num_image = 1

image_files = sorted(
    [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(".jpg")],
    key=lambda x: int(x.lower().replace("image", "").replace(".jpg", ""))
)

for image_name in image_files:
    if num_image > 10:
        break

    print(image_name)

    image_path = os.path.join(IMAGE_DIR, image_name)
    text_path = os.path.join(
        TEXT_DIR,
        os.path.splitext(image_name)[0] + ".txt"
    )

    if not os.path.exists(text_path):
        print(f"[WARN] Missing text file for {image_name}")
        continue

    # =========================
    # OCR USING OCRService
    # =========================
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    segments = OCRService.extract_text(
        image_bytes=image_bytes,
        preprocess=True,
        use_vietocr=True
    )

    ocr_text = OCRService.segments_to_text(segments)


    with open(text_path, "r", encoding="utf-8") as f:
        correct_text = f.read()

    ocr_text_norm = normalize_text(ocr_text)
    correct_text_norm = normalize_text(correct_text)


    #text_spliter = text_spliter(correct_text_norm)

    # WER OCR
    wer_score = wer(correct_text_norm, ocr_text_norm)
    correct_ratio_ocr = round(1 - wer_score, 4)

    vi_text, structure = text_spliter.split_text_for_bartpho(ocr_text_norm)

    #print(str(" ".join([ item["text"] for item in structure])))
    print(structure, type(structure))

    # BART POST-PROCESS
    bart_text = run_bart_model(vi_text)[0:-1]
    print(bart_text)


    merge_text = text_merger.merge_bartpho_result(structure, bart_text)
    wer_score_bart = wer(correct_text_norm, merge_text)
    correct_ratio_bart = round(1 - wer_score_bart, 4)

    records.append({
        "no.": index,
        "image_name": image_name,
        "correct_text": correct_text,
        "ocr_text": ocr_text,
        "correct_ratio_ocr": correct_ratio_ocr,
        "bart_text": bart_text,
        "correct_ratio_bart": correct_ratio_bart
    })

    index += 1
    num_image += 1


df = pd.DataFrame(records)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
