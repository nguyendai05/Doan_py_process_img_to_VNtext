from __future__ import annotations
from pathlib import Path
import re
import threading
from typing import Dict, Any, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # tokenizer + seq2seq model

class TranslationService:
    def __init__(
        self,
        model_path: str | Path = r"D:\translation_models\vinai-translate-vi2en-v2",  # path model local
        device: Optional[str] = None,
        max_input_tokens: int = 450,               # token cho mỗi chunk
        max_new_tokens: int = 256,                 # giới hạn output token
        num_beams: int = 4,                        # beam search (cân bằng chất lượng/tốc độ)
        batch_size: int = 8,                       # dịch theo batch để giảm số lần generate()
        print_chunks: bool = True,                 # in quá trình chia chunk + cắt theo word
    ):
        self.model_path = Path(model_path)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_input_tokens = max_input_tokens   #  chunk
        self.max_new_tokens = max_new_tokens       #  generate
        self.num_beams = num_beams
        self.batch_size = batch_size               #  batch
        self.print_chunks = print_chunks           # bật/tắt in chunk
        self.tokenizer = None                      # lazy-load tokenizer
        self.model = None                          # lazy-load model
        self._decoder_start_token_id = None        # id token để decoder bắt đầu bằng en_XX
        self._load_lock = threading.Lock()         #synchronized

    #  print cho chunk
    def _chunk_print(self, msg: str) -> None:
        if self.print_chunks:
            print(msg, flush=True)

    # 1) Load model lazy + thread
    def load_model(self) -> None:
        if self.model is not None and self.tokenizer is not None:     # đã load rồi thì thôi
            return
        with self._load_lock:                                         # chặn current load
            if self.model is not None and self.tokenizer is not None:
                return
            if not self.model_path.exists():                          # path fail
                raise FileNotFoundError(f"Model not found: {self.model_path}")

            # src_lang vi
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),                                  # load từ folder local
                local_files_only=True,
                src_lang="vi_VN",                                      # set ngôn ngữ nguồn
            )
            if self.device == "cuda" and not torch.cuda.is_available():
                self.device = "cpu"
            try:
                dtype = torch.float16 if self.device == "cuda" else torch.float32
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    str(self.model_path),                              # load từ folder local
                    local_files_only=True,
                    torch_dtype=dtype,
                ).to(self.device)
            except Exception:
                # fallback CPU nếu GPU fail
                self.device = "cpu"
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    str(self.model_path),
                    local_files_only=True,
                    torch_dtype=torch.float32,
                ).to(self.device)

            self.model.eval()

            #set decoder start = en_XX để output ra tiếng Anh
            self._decoder_start_token_id = self.tokenizer.lang_code_to_id["en_XX"]

    # 2) Chuẩn hoá + tách câu + đếm token
    @staticmethod
    def _normalize(text: str) -> str:
        text = text.strip()                    # bỏ space đầu/cuối
        text = re.sub(r"\s+", " ", text)       # gom nhiều whitespace về 1 space
        return text

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        # tách câu theo dấu và xuống dòng
        parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text)
        return [p.strip() for p in parts if p and p.strip()]  # lọc rỗng + strip từng phần

    def _count_tokens(self, text: str) -> int:
        # yêu cầu tokenizer đã load
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    # 3) Chunk theo token budget tránh mất chữ
    def split_into_chunks(self, text: str) -> List[str]:
        # tokenizerđếm token
        text = self._normalize(text)           # normalize input trước
        if not text:                           # input rỗng
            return []

        sentences = self._split_sentences(text)  # tách câu
        if not sentences:                        # nếu không tách được thì coi như 1 chunk
            return [text]

        chunks: List[str] = []                 # list output chunks
        current: List[str] = []                #  chunk hiện tại

        # in  chia chunk
        self._chunk_print(f"[chunk] max_input_tokens={self.max_input_tokens} | sentences={len(sentences)}")

        def flush(reason: str = "") -> None:
            # đẩy current thành 1 chunk and reset
            if current:
                out_chunk = " ".join(current).strip()
                chunks.append(out_chunk)
                #  in khi flush chunk
                if reason:
                    self._chunk_print(f"[chunk] flush -> ({reason}) | tokens={self._count_tokens(out_chunk)} | text={out_chunk}")
                else:
                    self._chunk_print(f"[chunk] flush -> tokens={self._count_tokens(out_chunk)} | text={out_chunk}")
                current.clear()

        for idx, sent in enumerate(sentences, start=1):
            sent_tokens = self._count_tokens(sent)

            #in từng câu + token
            self._chunk_print(f"[chunk] sent {idx}/{len(sentences)} | tokens={sent_tokens} | {sent}")

            # 1 câu > token budget -> cắt theo word kh mất text
            if sent_tokens > self.max_input_tokens:
                flush("before split-long-sentence")  #tách riêng, tránh dính với chunk trước
                self._chunk_print(f"[chunk] long sentence -> split by words | sent_tokens={sent_tokens}")

                words = sent.split()            # tách theo khoảng trắng
                buf: List[str] = []             # buffer cho đoạn cắt theo word

                for w in words:
                    cand = " ".join(buf + [w]).strip()  # thử thêm 1 từ
                    if self._count_tokens(cand) <= self.max_input_tokens:
                        buf.append(w)           # còn trong budget -> giữ
                        #  in gọn lúc ghép word
                        self._chunk_print(f"[chunk-word] + '{w}' | buf_tokens={self._count_tokens(cand)}")
                    else:
                        if buf:
                            out_buf = " ".join(buf).strip()
                            chunks.append(out_buf)  # flush buf thành chunk
                            # in lúc flush theo word
                            self._chunk_print(f"[chunk-word] flush -> tokens={self._count_tokens(out_buf)} | text={out_buf}")
                        buf = [w]               # bắt đầu buf mới với từ hiện tại
                        self._chunk_print(f"[chunk-word] new buf start with '{w}'")

                if buf:
                    out_buf = " ".join(buf).strip()
                    chunks.append(out_buf)  # flush phần còn lại
                    self._chunk_print(f"[chunk-word] flush(last) -> tokens={self._count_tokens(out_buf)} | text={out_buf}")
                continue

            # nếu current rỗng -> bắt đầu chunk mới
            if not current:
                current.append(sent)
                self._chunk_print(f"[chunk] start new chunk with sent {idx}")
                continue

            # ghép câu vào chunk hiện tại, > budget thì flush rồi create new chucnk
            cand = " ".join(current + [sent]).strip()
            cand_tokens = self._count_tokens(cand)

            if cand_tokens <= self.max_input_tokens:
                current.append(sent)            # còn budget -> ghép luôn
                self._chunk_print(f"[chunk] append -> chunk_tokens={cand_tokens}")
            else:
                flush("budget exceeded")        # (NEW) vượt budget -> chốt chunk cũ
                current.append(sent)            # mở chunk mới
                self._chunk_print(f"[chunk] start new chunk (after flush) with sent {idx}")

        flush("end")                              # chốt chunk cuối
        return chunks

    # 4 giữ nguyên dữ liệu quan trọng
    @staticmethod
    def _extract_invariants(text: str) -> List[str]:
        patterns = [
            r"(https?://[^\s]+|www\.[^\s]+)",  # URL
            r"\b[\w.\-+]+@[\w.\-]+\.\w+\b",  # Email
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",  # yyyy-mm-dd   <-- THÊM DÒNG NÀY
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # dd-mm-yyyy
            r"\b\d{1,2}:\d{2}(?::\d{2})?\b",  # HH:MM(:SS)
            r"\b\d+(?:[.,]\d+)*(?:%|\b)",  # numbers + optional %
            r"\b[A-Z]{1,6}(?:\d{0,3})?(?:-\d{1,6}){1,3}\b",  # codes: A-203, R2-101, HD-2026-001...
        ]

        found: List[str] = []
        for p in patterns:
            found.extend(re.findall(p, text))               # gom tất cả match

        def clean_item(s: str) -> str:
            # bỏ dấu câu hay dính ở cuối link/email khi đứng cuối câu
            return s.strip().rstrip(".,;:!?)]}\"'")

        cleaned = [clean_item(x) for x in found if clean_item(x)]
        return list(dict.fromkeys(cleaned))                 # unique nhưng giữ thứ tự tương đối

    @staticmethod
    def _digits_only(s: str) -> str:
        return re.sub(r"\D", "", s)                         # lấy riêng chữ số để check tolerant

    def check_invariants(self, src_text: str, out_text: str) -> Dict[str, Any]:
        inv = self._extract_invariants(src_text)            # lấy list invariant từ input
        out_digits = self._digits_only(out_text)            # digits-only của output để check số

        missing: List[str] = []
        for item in inv:
            if item in out_text:                            # khớp strict substring
                continue

            d = self._digits_only(item)                     # nếu là số (có digits)
            if d and d in out_digits:                       # tolerant: số tồn tại dù mất dấu , .
                continue

            missing.append(item)                            # không thấy -> đánh dấu thiếu

        return {"count": len(inv), "missing": missing, "ok": len(missing) == 0}


    # 5) Translate batch (tokenize -> generate -> decode)
    def _translate_batch(self, texts: List[str]) -> List[str]:
        if not texts:
            return []

        # tokenize batch: padding để cùng shape, truncation safety max 512
        enc = self.tokenizer(
            texts,
            return_tensors="pt",                            # output tensor cho PyTorch
            padding=True,
            truncation=True,                                # cắt nếu vượt max_length
            max_length=512,                                 # giới hạn encoder của mBART
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}  # chuyển input lên cpu/cuda

        with torch.inference_mode():
            out_ids = self.model.generate(
                **enc,                                      # input_ids, .
                decoder_start_token_id=self._decoder_start_token_id,  # bắt đầu bằng en_XX
                num_beams=self.num_beams,                   # beam search
                early_stopping=True,                        # dừng sớm khi xong
                max_new_tokens=self.max_new_tokens,         # giới hạn output token
            )

        outs = self.tokenizer.batch_decode(out_ids, skip_special_tokens=True)  # decode token ids
        return [self._normalize(o) for o in outs]            # normalize output cho sạch


    # 6) translate
    def translate(self, text: str) -> Dict[str, Any]:
        self.load_model()                                    # đảm bảo model/tokenizer đã load

        raw = self._normalize(text)                           # normalize input
        if not raw:                                           # rỗng -> trả fail gọn
            return {"success": False, "error": "Empty text", "time_ms": 0}

        chunks = self.split_into_chunks(raw)                  # chunk theo token budget
        if not chunks:                                        # không có chunk -> fail
            return {"success": False, "error": "No valid text", "time_ms": 0}

        translated_chunks: List[str] = []
        for i in range(0, len(chunks), self.batch_size):      # chia batch
            batch = chunks[i : i + self.batch_size]           # lấy batch hiện tại
            translated_chunks.extend(self._translate_batch(batch))  # dịch batch và nối kết quả

        translated_text = self._normalize(" ".join(t for t in translated_chunks if t))  # ghép output
        invariants = self.check_invariants(raw, translated_text)  # check dữ liệu quan trọng

        return {
            "success": True,
            "translated_text": translated_text,
            "source_lang": "vi",                               # cố định vi->en cho model này
            "dest_lang": "en",
            "device": self.device,                             # cpu/cuda
            "chunks_count": len(chunks),                       # số chunk đã dùng
            "invariants": invariants,                           # ok/missing/count
        }
translation_service = TranslationService()

# tesst
def _run_translation_service_self_test() -> None:
    print("\n========== TranslationService SELF-TEST ==========\n", flush=True)

    # Test data: có dấu câu, xuống dòng, URL/email, ngày giờ, số %, code...
    sample_text = """
    Xin chào bạn! Hôm nay là 2026-01-06.
    Liên hệ: test.user+abc@gmail.com hoặc www.example.com.
    Link: https://example.com/a/b?x=1,y=2.
    Mã: HD-2026-001, A-203.
    Thời gian: 13:45. Tỉ lệ 12.5%.
    Dòng 2: Đây là một câu dài để thử chia chunk theo token budget. Cảm ơn!
    """.strip()

    # 0) Khởi tạo service test (bật in chunk nếu bạn muốn thấy quá trình chia)
    svc = TranslationService(
        model_path=r"D:\translation_models\vinai-translate-vi2en-v2",
        max_input_tokens=80,     # giảm để dễ thấy chunk
        batch_size=2,
        print_chunks=True,       # bật in ra đoạn chia chunk + ghép word
    )

    # 1) Test _normalize
    norm = svc._normalize("   A   B \n  C   ")
    assert norm == "A B C", f"_normalize FAIL: got={norm!r}"
    print("[OK] _normalize", flush=True)

    # 2) Test _split_sentences
    sents = svc._split_sentences("Câu 1. Câu 2!\nCâu 3?  Câu 4。")
    assert len(sents) == 4, f"_split_sentences FAIL: len={len(sents)} sents={sents}"
    print("[OK] _split_sentences", flush=True)

    # 3) Test _extract_invariants
    inv = svc._extract_invariants(sample_text)
    # chỉ cần check có chứa một vài invariant chính
    must_have = ["2026-01-06", "test.user+abc@gmail.com", "www.example.com", "HD-2026-001", "13:45", "12.5%"]
    for x in must_have:
        assert x in inv, f"_extract_invariants FAIL: missing {x}"
    print("[OK] _extract_invariants", flush=True)

    # 4) Test check_invariants (case OK)
    inv_check_ok = svc.check_invariants(sample_text, sample_text)
    assert inv_check_ok["ok"] is True, f"check_invariants FAIL (expected ok=True): {inv_check_ok}"
    print("[OK] check_invariants (ok case)", flush=True)

    # 5) Test check_invariants (case missing)
    out_missing = "Xin chào! Hôm nay là 2026-01-06. Liên hệ: email bị mất."
    inv_check_bad = svc.check_invariants(sample_text, out_missing)
    assert inv_check_bad["ok"] is False and len(inv_check_bad["missing"]) > 0, \
        f"check_invariants FAIL (expected missing): {inv_check_bad}"
    print("[OK] check_invariants (missing case)", flush=True)

    # 6) Model-dependent tests: load_model, split_into_chunks, _translate_batch, translate
    print("\n--- Model-dependent tests ---", flush=True)
    try:
        svc.load_model()
        print(f"[OK] load_model | device={svc.device}", flush=True)

        # split_into_chunks cần tokenizer -> test chunking theo token
        chunks = svc.split_into_chunks(sample_text)
        assert len(chunks) > 0, "split_into_chunks FAIL: no chunks"
        print(f"[OK] split_into_chunks | chunks_count={len(chunks)}", flush=True)

        # _translate_batch test nhỏ (1-2 chunk đầu)
        small_batch = chunks[: min(2, len(chunks))]
        out_batch = svc._translate_batch(small_batch)
        assert len(out_batch) == len(small_batch), "_translate_batch FAIL: output size mismatch"
        print("[OK] _translate_batch", flush=True)

        # translate test đầy đủ
        result = svc.translate(sample_text)
        assert result.get("success") is True, f"translate FAIL: {result}"
        assert isinstance(result.get("translated_text"), str) and result["translated_text"].strip(), \
            "translate FAIL: empty translated_text"
        print("[OK] translate", flush=True)

        # In nhanh kết quả để bạn nhìn
        print("\n--- Translate RESULT (preview) ---", flush=True)
        print("device:", result.get("device"), flush=True)
        print("chunks_count:", result.get("chunks_count"), flush=True)
        print("invariants:", result.get("invariants"), flush=True)
        print("translated_text (first 400 chars):", result["translated_text"][:400], flush=True)

    except FileNotFoundError as e:
        print(f"[SKIP] Model not found -> bỏ qua test dịch: {e}", flush=True)
    except Exception as e:
        print(f"[FAIL] Model-dependent tests error: {type(e).__name__}: {e}", flush=True)
        raise

    print("\n========== SELF-TEST DONE ==========\n", flush=True)


# Nếu chạy file trực tiếp: python translation_service.py
# Java tương đương: public static void main(String[] args) { ... }
if __name__ == "__main__":
    _run_translation_service_self_test()

