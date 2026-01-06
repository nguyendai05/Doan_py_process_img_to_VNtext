# app/services/translation_service.py
"""
Model local: vinai-translate-vi2en-v2

Mục tiêu:
- Load mBART đúng cách: src_lang + decoder_start_token_id (để ra đúng EN)
- Chia chunk theo TOKEN budget (tránh truncation/mất chữ)
- Dịch theo batch (nhanh hơn)
- Tính toán metadata + invariant-check ngay trong service (không phụ thuộc UI)
"""

from __future__ import annotations

from pathlib import Path                      # dùng Path để quản lý đường dẫn model local cho rõ ràng
import logging                               # logging để debug khi deploy server
import re                                    # regex để tách câu + kiểm invariants
import threading                             # lock để tránh load model nhiều lần khi server nhiều request
import time                                  # đo time_ms cho mỗi lần translate
from typing import Dict, Any, List, Optional, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)          # logger theo module (chuẩn logging Python)


class TranslationService:
    def __init__(
        self,
        model_path: str | Path = "D:/translation_models/vinai-translate-vi2en-v2",
        device: Optional[str] = None,
        max_input_tokens: int = 450,          # budget token input (an toàn < 512 token encoder)
        max_new_tokens: int = 256,            # giới hạn token output (tránh câu quá dài gây chậm)
        num_beams: int = 4,                   # beam search: 4 là cân bằng chất lượng/tốc độ
        batch_size: int = 8,                  # dịch theo batch để nhanh hơn
    ):
        self.model_path = Path(model_path)    # chuyển sang Path để check exists + join path thuận tiện
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")  # auto GPU nếu có

        self.max_input_tokens = max_input_tokens
        self.max_new_tokens = max_new_tokens
        self.num_beams = num_beams
        self.batch_size = batch_size

        self.tokenizer: Optional[AutoTokenizer] = None   # lazy-load tokenizer
        self.model: Optional[AutoModelForSeq2SeqLM] = None  # lazy-load model
        self._decoder_start_token_id: Optional[int] = None  # token id để decoder bắt đầu bằng en_XX

        self._load_lock = threading.Lock()   # lock để thread-safe khi load model (giống synchronized Java)

        logger.info("TranslationService init | device=%s | model_path=%s", self.device, self.model_path)

    # =========================================================
    # 1) Load model (lazy + thread-safe)
    # =========================================================
    def load_model(self) -> None:
        # Nếu đã load rồi thì bỏ qua (tối ưu thời gian)
        if self.model is not None and self.tokenizer is not None:
            return

        # Dùng lock để tránh 2 request cùng lúc vào, load model 2 lần
        with self._load_lock:
            # Double-check sau khi đã acquire lock (pattern chuẩn)
            if self.model is not None and self.tokenizer is not None:
                return

            # Nếu folder model không tồn tại => báo lỗi rõ ràng cho bạn debug
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found at: {self.model_path}")

            logger.info("Loading model from: %s", self.model_path)

            # Quan trọng cho mBART: src_lang giúp tokenizer set ngôn ngữ nguồn đúng (vi_VN)
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                local_files_only=True,
                src_lang="vi_VN",
            )

            # Dùng float16 khi GPU để tăng tốc; CPU thì float32 để ổn định
            dtype = torch.float16 if self.device == "cuda" else torch.float32

            # Load model từ local (không download)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                str(self.model_path),
                local_files_only=True,
                torch_dtype=dtype,
            ).to(self.device)

            self.model.eval()  # set inference mode (tương tự disable dropout)

            # Quan trọng cho mBART: decoder_start_token_id = en_XX để output ra tiếng Anh
            try:
                self._decoder_start_token_id = self.tokenizer.lang_code_to_id["en_XX"]
            except Exception as e:
                raise ValueError("Missing lang_code_to_id['en_XX'] in tokenizer.") from e

            logger.info("✓ Model loaded | decoder_start_token_id=%s", self._decoder_start_token_id)

    # =========================================================
    # 2) Normalize + sentence split + token count
    # =========================================================
    @staticmethod
    def _normalize(text: str) -> str:
        # Chuẩn hoá: bỏ space đầu/cuối + gom nhiều khoảng trắng => 1 space
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        # Tách câu theo dấu .!? và xuống dòng để chunk theo ngữ nghĩa (ít phá nghĩa)
        parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
        return [p.strip() for p in parts if p and p.strip()]

    def _count_tokens(self, text: str) -> int:
        # Đếm tokens để đảm bảo chunk không vượt budget => tránh truncation
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    # =========================================================
    # 3) Chunking theo token budget (tránh mất chữ)
    # =========================================================
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Chunk theo câu, nhưng giới hạn theo token budget:
        - Nếu câu đơn lẻ vượt budget => cắt theo từ.
        - Nếu ghép thêm câu vượt budget => flush chunk hiện tại.
        """
        text = self._normalize(text)
        if not text:
            return []

        sentences = self._split_sentences(text)
        if not sentences:
            return [text]

        chunks: List[str] = []
        current: List[str] = []

        def flush():
            # Đẩy chunk hiện tại vào danh sách chunks
            if current:
                chunks.append(" ".join(current).strip())
                current.clear()

        for sent in sentences:
            # 1) Nếu 1 câu quá dài theo token => cắt theo từ
            if self._count_tokens(sent) > self.max_input_tokens:
                flush()  # đảm bảo chunk trước đó không bị dính với câu dài
                words = sent.split()

                buf: List[str] = []
                for w in words:
                    cand = (" ".join(buf + [w])).strip()
                    if self._count_tokens(cand) <= self.max_input_tokens:
                        buf.append(w)
                    else:
                        if buf:
                            chunks.append(" ".join(buf).strip())
                        buf = [w]
                if buf:
                    chunks.append(" ".join(buf).strip())
                continue

            # 2) Nếu current rỗng => bắt đầu chunk mới
            if not current:
                current.append(sent)
                continue

            # 3) Thử ghép câu vào chunk hiện tại (theo token budget)
            cand = (" ".join(current + [sent])).strip()
            if self._count_tokens(cand) <= self.max_input_tokens:
                current.append(sent)
            else:
                flush()
                current.append(sent)

        flush()
        return chunks

    # =========================================================
    # 4) Invariant check (kiểm “đúng dữ liệu” cho OCR)
    # =========================================================
    @staticmethod
    def _extract_invariants(text: str) -> List[str]:
        """
        Trích các chuỗi "nên giữ nguyên" trong bản dịch:
        - URL, email
        - date/time
        - numbers/percent
        - mã phòng/mã dạng A-203, B-12, ...
        """
        patterns = [
            r"(https?://[^\s]+|www\.[^\s]+)",                 # URL
            r"\b[\w.\-+]+@[\w.\-]+\.\w+\b",                   # Email
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",               # yyyy-mm-dd / yyyy/mm/dd
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",             # dd-mm-yyyy / dd/mm/yyyy
            r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b",                 # dd.mm.yyyy
            r"\b\d{1,2}:\d{2}(?::\d{2})?\b",                  # time: HH:MM(:SS)
            r"\b\d+(?:[.,]\d+)*%?\b",                         # numbers + optional %
            r"\b[A-Z]{1,3}-\d{1,4}\b",                        # room/code: A-203, B-12, R2-101
        ]

        found: List[str] = []
        for p in patterns:
            found.extend(re.findall(p, text))

        # Làm sạch những ký tự dấu câu hay bị dính ở cuối URL/email khi đứng cuối câu
        def clean_item(s: str) -> str:
            return s.strip().rstrip(".,;:!?)]}\"'")  # remove trailing punctuation often attached by NLP

        cleaned = [clean_item(x) for x in found if clean_item(x)]
        # unique + giữ thứ tự tương đối (dùng dict trick)
        return list(dict.fromkeys(cleaned))

    @staticmethod
    def _digits_only(s: str) -> str:
        # Dùng cho numbers: nếu model bỏ dấu phẩy/chấm thì vẫn có thể check bằng digits
        return re.sub(r"\D", "", s)

    def check_invariants(self, src_text: str, out_text: str) -> Dict[str, Any]:
        """
        Kiểm tra các invariant có còn trong output không.
        - URL/email/date/time: check strict substring
        - numbers: check strict OR digits-only (tolerant hơn)
        """
        inv = self._extract_invariants(src_text)

        missing: List[str] = []
        for item in inv:
            if item in out_text:
                continue

            # với số: cho phép tồn tại dạng digits-only trong output (giảm false negative)
            if self._digits_only(item):
                if self._digits_only(item) and self._digits_only(item) in self._digits_only(out_text):
                    continue

            missing.append(item)

        return {
            "count": len(inv),
            "missing": missing,
            "ok": len(missing) == 0,
        }

    # =========================================================
    # 5) Translate batch
    # =========================================================
    def _translate_batch(self, texts: List[str]) -> List[str]:
        if not texts:
            return []

        # Tokenize batch: padding để cùng shape, truncation safety cho encoder 512
        enc = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        # Move tensors lên GPU/CPU đúng device
        enc = {k: v.to(self.device) for k, v in enc.items()}

        # inference_mode: nhanh hơn + không giữ graph
        with torch.inference_mode():
            out_ids = self.model.generate(
                **enc,
                decoder_start_token_id=self._decoder_start_token_id,  # bắt buộc để ra English
                num_beams=self.num_beams,                            # beam search
                early_stopping=True,
                max_new_tokens=self.max_new_tokens,                  # giới hạn output tokens
            )

        # Decode token ids thành string tiếng Anh
        outs = self.tokenizer.batch_decode(out_ids, skip_special_tokens=True)
        return [self._normalize(o) for o in outs]  # normalize output để sạch

    # =========================================================
    # 6) Public API: translate() trả đủ metadata + invariant report
    # =========================================================
    def translate(self, text: str, dest_lang: str = "en", src_lang: str = "vi") -> Dict[str, Any]:
        start = time.perf_counter()  # bắt đầu đo thời gian (ms) cho toàn bộ request
        try:
            # Validate input
            if not text or not text.strip():
                return {"success": False, "error": "Empty text"}

            # Model local này chỉ hỗ trợ vi -> en
            if src_lang != "vi" or dest_lang != "en":
                return {"success": False, "error": "This local model only supports vi -> en."}

            self.load_model()  # đảm bảo tokenizer/model đã sẵn sàng

            raw = self._normalize(text)  # normalize trước khi chunk
            chunks = self.split_into_chunks(raw)  # chunk theo token budget để không mất chữ

            if not chunks:
                return {"success": False, "error": "No valid text"}

            # Translate theo batch để nhanh hơn (ít call generate hơn)
            translated_chunks: List[str] = []
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i : i + self.batch_size]
                translated_chunks.extend(self._translate_batch(batch))

            result = self._normalize(" ".join([t for t in translated_chunks if t]))
            if not result:
                return {"success": False, "error": "No translation result"}

            # Kiểm “đúng dữ liệu” (invariants) ngay trong service
            inv_report = self.check_invariants(raw, result)

            # Nếu thiếu invariant => trả warning (để UI/FE muốn hiển thị thì hiển thị; không bắt buộc)
            warning = None
            if not inv_report["ok"]:
                warning = "Translation may have altered critical data (numbers/dates/urls/emails/codes)."

            time_ms = int((time.perf_counter() - start) * 1000)  # tổng thời gian xử lý tính bằng ms

            return {
                "success": True,
                "translated_text": result,
                "source_lang": "vi",
                "dest_lang": "en",
                "device": self.device,             # metadata: CPU/GPU
                "chunks_count": len(chunks),       # metadata: số chunk
                "time_ms": time_ms,                # metadata: thời gian chạy
                "invariants": inv_report,          # report: count/missing/ok
                "warning": warning,                # warning nếu thiếu dữ liệu quan trọng
            }

        except Exception as e:
            logger.error("Translation error: %s", str(e), exc_info=True)
            time_ms = int((time.perf_counter() - start) * 1000)
            return {"success": False, "error": f"Translation failed: {str(e)}", "time_ms": time_ms}

    # Debug helper: xem chunk trước khi dịch (phục vụ test/demo)
    def preview_chunks(self, text: str) -> List[Dict[str, Any]]:
        self.load_model()                       # cần tokenizer để đếm token
        raw = self._normalize(text)             # normalize cho ổn định
        chunks = self.split_into_chunks(raw)    # chunk logic chạy trong service

        return [
            {
                "index": i + 1,
                "chars": len(c),
                "tokens": self._count_tokens(c),
                "text": c,
            }
            for i, c in enumerate(chunks)
        ]

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        return {"vi": "Vietnamese", "en": "English"}


# Singleton instance dùng chung toàn app (tương tự static singleton trong Java)
translation_service = TranslationService()
