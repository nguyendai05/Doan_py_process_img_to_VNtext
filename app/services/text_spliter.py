import re
import unicodedata
from typing import List, Dict, Tuple

# =========================
# REGEX
# =========================

TOKEN_REGEX = re.compile(
    r"\d+([.,]\d+)?|"               # number
    r"[A-Za-zÀ-Ỹà-ỹĂăÂâĐđÊêÔôƠơƯư]+|" # words (vi + en)
    r"\s+|"                         # whitespace
    r"[^\w\s]",                     # punctuation
    re.UNICODE
)

ENGLISH_REGEX = re.compile(r"^[A-Za-z]+$")
NUMBER_REGEX = re.compile(r"^\d+([.,]\d+)?$")


# =========================
# UTILS
# =========================

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_vietnamese(word: str) -> bool:
    return any(ord(c) > 127 for c in word)


def classify_token(token: str) -> str:
    if NUMBER_REGEX.fullmatch(token):
        return "number"

    if ENGLISH_REGEX.fullmatch(token):
        return "english"

    if token.strip() and is_vietnamese(token):
        return "vietnamese"

    if token.isspace():
        return "space"

    return "other"


# =========================
# MAIN API
# =========================

def split_text_for_bartpho(text: str) -> Tuple[str, List[Dict]]:
    """
    Input:
        raw OCR text (str)

    Output:
        bartpho_input (str): ONLY Vietnamese text
        structure (list): layout info for merging
    """
    text = normalize_text(text)

    tokens = []
    for m in TOKEN_REGEX.finditer(text):
        tok = m.group(0)
        tokens.append({
            "text": tok,
            "type": classify_token(tok)
        })

    structure = []
    vietnamese_parts = []

    for token in tokens:
        if token["type"] == "vietnamese":
            structure.append({
                "type": "vietnamese",
                "index": len(vietnamese_parts)
            })
            vietnamese_parts.append(token["text"])
        else:
            structure.append({
                "type": "raw",
                "text": token["text"]
            })

    # 👉 BartPho nhận MỘT chuỗi duy nhất
    bartpho_input = " ".join(vietnamese_parts)

    return bartpho_input, structure
