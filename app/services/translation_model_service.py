from __future__ import annotations
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Tuple, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class TranslationModelService:
    _lock = threading.Lock()
    _tokenizer = None
    _model = None
    _device: Optional[torch.device] = None

    def __init__(
        self,
        model_dir: str | Path = r"D:\FinetuneWork\opus-vi-en-100k-final",
        max_tokens_per_chunk: int = 420,     # safe < 512
        batch_size: int = 12,
        max_batch_tokens: int = 2400,
        max_new_tokens: int = 220,
        num_beams: int = 4,
    ):
        self.model_dir = str(model_dir)
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.batch_size = batch_size
        self.max_batch_tokens = max_batch_tokens
        self.max_new_tokens = max_new_tokens
        self.num_beams = num_beams

        # optional: words you mentioned; used only to help spacing when reinserting
        self._preps = {
            "in", "of", "for", "on", "at", "to", "from", "by", "with", "as",
            "into", "over", "under", "about", "before", "after", "during"
        }

    # ------------------ LOAD ONCE ------------------
    @classmethod
    def _ensure_loaded(cls, model_dir: str) -> None:
        if cls._model is not None and cls._tokenizer is not None:
            return

        with cls._lock:
            if cls._model is not None and cls._tokenizer is not None:
                return

            print(" Loading VI→EN model...")
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            dtype = torch.float16 if device.type == "cuda" else torch.float32

            tok = AutoTokenizer.from_pretrained(model_dir)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_dir, torch_dtype=dtype)
            model.to(device)
            model.eval()

            cls._tokenizer = tok
            cls._model = model
            cls._device = device

            print(f"✅ Model loaded on {device.type.upper()} (dtype={dtype})")

    def _clean_keep_format(self, text: str) -> str:
        s = (text or "").replace("\r\n", "\n")

        # keep newlines; normalize spaces per line
        lines = s.splitlines()
        lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in lines]
        s = "\n".join(lines)

        # remove space before punctuation
        s = re.sub(r" +([.,;:!?])", r"\1", s)

        # max 2 blank lines
        s = re.sub(r"\n{3,}", "\n\n", s)

        return s.strip()

    # ------------------ TOKEN UTILS ------------------
    def _tok_len(self, tok, s: str) -> int:
        return len(tok(s, add_special_tokens=True).input_ids)

    # ------------------ SENTENCE SPLIT (keep separators) ------------------
    def _split_sentences_keep_seps(self, text: str) -> Tuple[List[str], List[str]]:

        s = (text or "").replace("\r\n", "\n")

        sentences: List[str] = []
        seps: List[str] = []

        def is_end_punct(ch: str) -> bool:
            return ch in ".!?:…"

        i = 0
        n = len(s)
        start = 0
        while i < n:
            if is_end_punct(s[i]):
                sent = s[start:i + 1]
                j = i + 1
                while j < n and s[j].isspace():
                    j += 1
                sep = s[i + 1:j]
                if sent.strip():
                    sentences.append(sent.strip())
                    seps.append(sep)
                start = j
                i = j
            else:
                i += 1

        # tail (no ending punctuation)
        if start < n and s[start:].strip():
            sentences.append(s[start:].strip())
            seps.append("")

        return sentences, seps

    def _split_long_by_words(self, tok, sentence: str) -> List[str]:
        if self._tok_len(tok, sentence) <= self.max_tokens_per_chunk:
            return [sentence]

        words = sentence.split()
        parts: List[str] = []
        cur = ""
        for w in words:
            cand = (cur + " " + w) if cur else w
            if self._tok_len(tok, cand) <= self.max_tokens_per_chunk:
                cur = cand
            else:
                if cur:
                    parts.append(cur)
                cur = w
        if cur:
            parts.append(cur)
        return parts

    def _build_chunks_from_sentences(self, tok, sentences: List[str], seps: List[str]) -> List[str]:

        chunks: List[str] = []
        cur = ""

        for sent, sep in zip(sentences, seps):
            piece = sent + sep  # keep original spacing/newlines after sentence

            if not cur:
                # sentence itself too long -> split by words
                if self._tok_len(tok, piece) > self.max_tokens_per_chunk:
                    parts = self._split_long_by_words(tok, sent)
                    for i, p in enumerate(parts):
                        if i == len(parts) - 1:
                            chunks.append(p + sep)
                        else:
                            chunks.append(p + " ")
                    cur = ""
                else:
                    cur = piece
                continue

            cand = cur + piece
            if self._tok_len(tok, cand) <= self.max_tokens_per_chunk:
                cur = cand
            else:
                chunks.append(cur)
                # start new chunk with this sentence (or its word-splits)
                if self._tok_len(tok, piece) > self.max_tokens_per_chunk:
                    parts = self._split_long_by_words(tok, sent)
                    for i, p in enumerate(parts):
                        if i == len(parts) - 1:
                            chunks.append(p + sep)
                        else:
                            chunks.append(p + " ")
                    cur = ""
                else:
                    cur = piece

        if cur:
            chunks.append(cur)

        return chunks

    # ------------------ FIND SPECIAL SPANS (per chunk) ------------------
    def _find_entities_spans(self, s: str) -> List[Tuple[int, int, str, str]]:

        patterns = [
            ("NL",    r"\n+"),
            ("URL",   r"(https?://\S+|www\.\S+)"),
            ("EMAIL", r"[\w.\-]+@[\w.\-]+\.\w+"),
            ("DATE1", r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),                   # 2022-04-19
            ("DATE2", r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b"),            # 19/04/2022 or 2/9
            ("DATE3", r"\bngày\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}\b"),# ngày ... tháng ... năm ...
            ("TIME1", r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),                      # 12:30:10
            ("TIME2", r"\b\d{1,2}\s*giờ(?:\s*\d{1,2}\s*phút)?\b"),           # 8 giờ 15 phút
            ("NUM",   r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?%?\b"),           # 1.250.000, 12,5%, 80%
        ]

        cands: List[Tuple[int, int, str, str]] = []
        for typ, pat in patterns:
            for m in re.finditer(pat, s, flags=re.IGNORECASE):
                cands.append((m.start(), m.end(), typ, m.group(0)))

        cands.sort(key=lambda x: (x[0], -(x[1] - x[0])))

        kept: List[Tuple[int, int, str, str]] = []
        last_end = -1
        for st, ed, typ, val in cands:
            if st >= last_end:
                kept.append((st, ed, typ, val))
                last_end = ed
            else:
                continue

        return kept

    # ------------------ SPLIT CHUNK INTO SEGMENTS + ENTITIES ------------------
    def _split_chunk_by_entities(
        self, chunk: str
    ) -> Tuple[List[str], List[str], List[Tuple[bool, bool]]]:

        spans = self._find_entities_spans(chunk)
        segments: List[str] = []
        entities: List[str] = []
        glue: List[Tuple[bool, bool]] = []

        cursor = 0
        for st, ed, _typ, val in spans:
            left = chunk[cursor:st]

            had_before = (len(left) > 0 and left[-1].isspace())
            had_after = (ed < len(chunk) and chunk[ed].isspace())

            segments.append(left)
            entities.append(val)
            glue.append((had_before, had_after))
            cursor = ed

        segments.append(chunk[cursor:])
        return segments, entities, glue

    # ------------------ BATCH TRANSLATE (only text segments) ------------------
    def _make_batches(self, texts: List[str], toks: List[int]) -> List[List[str]]:
        batches: List[List[str]] = []
        cur: List[str] = []
        cur_sum = 0
        for t, l in zip(texts, toks):
            if not cur:
                cur = [t]
                cur_sum = l
                continue
            if (len(cur) + 1 > self.batch_size) or (cur_sum + l > self.max_batch_tokens):
                batches.append(cur)
                cur = [t]
                cur_sum = l
            else:
                cur.append(t)
                cur_sum += l
        if cur:
            batches.append(cur)
        return batches

    def _translate_texts(self, texts: List[str]) -> List[str]:

        tok = self.__class__._tokenizer
        model = self.__class__._model
        device = self.__class__._device

        out = texts[:]
        idx_map: List[int] = []
        to_tr: List[str] = []
        for i, t in enumerate(texts):
            if t and t.strip():
                idx_map.append(i)
                to_tr.append(t)

        if not to_tr:
            return out

        lens = [self._tok_len(tok, t) for t in to_tr]
        batches = self._make_batches(to_tr, lens)

        produced: List[str] = []
        for batch in batches:
            inputs = tok(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(device)

            with torch.inference_mode():
                gen = model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    num_beams=self.num_beams,
                    do_sample=False,
                    early_stopping=True,
                    # keep these gentle to reduce "missing words"
                    no_repeat_ngram_size=2,
                    repetition_penalty=1.05,
                    length_penalty=1.0,
                )

            produced.extend(tok.batch_decode(gen, skip_special_tokens=True))

        for i, tr in zip(idx_map, produced):
            out[i] = tr

        return out

    # ------------------ REINSERT ENTITIES (smart spacing) ------------------
    def _needs_space(self, a: str, b: str) -> bool:
        if not a or not b:
            return False
        if a[-1].isspace() or b[0].isspace():
            return False

        # avoid wordword / 2022abc sticking
        if a[-1].isalnum() and b[0].isalnum():
            return True

        # if last word is a preposition, prefer space before entity/word
        last_word = re.findall(r"[A-Za-z]+$", a.strip())
        if last_word and last_word[0].lower() in self._preps and b[0].isalnum():
            return True

        return False

    def _merge_segments_entities(
        self,
        segs_tr: List[str],
        entities: List[str],
        glue: List[Tuple[bool, bool]],
    ) -> str:
        out: List[str] = []

        for i in range(len(entities)):
            left = segs_tr[i] or ""
            ent = entities[i] or ""
            right = segs_tr[i + 1] or ""
            had_before, had_after = glue[i]

            out.append(left)

            # before entity
            if had_before or self._needs_space(left, ent):
                if out and out[-1] and not out[-1].endswith((" ", "\n", "\t")):
                    out.append(" ")

            out.append(ent)

            # after entity (avoid duplicating if right already begins with whitespace/newline)
            if had_after or self._needs_space(ent, right):
                if right and not right.startswith((" ", "\n", "\t")):
                    out.append(" ")

        out.append(segs_tr[-1] or "")
        return "".join(out)

    # ------------------ TRANSLATE (chunk-based) ------------------
    def translate(self, text: str) -> Dict[str, Any]:
        if not (text or "").strip():
            return {"success": False, "translated_text": "", "device": "cpu", "chunks_count": 0}

        self._ensure_loaded(self.model_dir)
        tok = self.__class__._tokenizer
        device = self.__class__._device

        # 1) split into sentences (only for building chunks)
        sentences, seps = self._split_sentences_keep_seps(text)

        # 2) build chunks by concatenating sentences until token limit
        chunks = self._build_chunks_from_sentences(tok, sentences, seps)

        # 3) for each chunk: split into segments/entities (entities NOT translated)
        chunk_meta: List[Dict[str, Any]] = []
        all_segments: List[str] = []
        owner: List[Tuple[int, int]] = []  # (chunk_index, segment_index)
        for ci, ch in enumerate(chunks):
            segs, ents, glue = self._split_chunk_by_entities(ch)
            chunk_meta.append({"segments": segs, "entities": ents, "glue": glue})
            for si, seg in enumerate(segs):
                all_segments.append(seg)
                owner.append((ci, si))

        # 4) translate all segments (batch)
        all_translated = self._translate_texts(all_segments)

        # 5) put translated segments back to chunks
        for (ci, si), tr in zip(owner, all_translated):
            original = chunk_meta[ci]["segments"][si]
            if original and original.strip():
                chunk_meta[ci]["segments"][si] = tr
            else:
                chunk_meta[ci]["segments"][si] = original  # keep whitespace-only exactly

        # 6) rebuild chunks with entities reinserted
        rebuilt_chunks: List[str] = []
        for meta in chunk_meta:
            rebuilt = self._merge_segments_entities(meta["segments"], meta["entities"], meta["glue"])
            rebuilt_chunks.append(rebuilt)

        final_text = self._clean_keep_format("".join(rebuilt_chunks))

        return {
            "success": True,
            "translated_text": final_text,
            "device": device.type if device else "cpu",
            "chunks_count": len(chunks),
        }

    # TEST ------------------
    @staticmethod
    def main() -> None:
        svc = TranslationModelService(
            model_dir=r"D:\Models_dich\opus-mt-vi-en",
            max_tokens_per_chunk=420,
            batch_size=12,
            max_batch_tokens=2400,
            max_new_tokens=220,
            num_beams=4,
        )

        test_text = (
            "Kính gửi anh/chị,\n\n"
            "Cuộc họp sẽ bắt đầu lúc 08:15 ngày 19/04/2022 tại phòng A-302.\n"
            "Nếu anh/chị không tham gia được, vui lòng phản hồi qua email: support-team.vn@company.com.\n"
            "Tài liệu tham khảo: https://example.com/docs?id=123&lang=vi và www.test-site.org/help.\n\n"
            "Ngân sách dự án là 1.250.000 VND (tăng 12,5% so với quý trước).\n"
            "Mã đơn: HD-2022-0007, hạn xử lý trước 2022-04-19 12:30:10.\n"
            "- Mục 1: Hoàn thành 80%.\n"
            "- Mục 2: Dự kiến 2/9 sẽ bàn giao.\n"
        )

        print("=" * 80)
        print("ORIGINAL:\n", test_text)
        res = svc.translate(test_text)
        print("\nTRANSLATED:\n", res["translated_text"])
        print("\nMETA:", {k: v for k, v in res.items() if k != "translated_text"})
        print("=" * 80)


if __name__ == "__main__":
    TranslationModelService.main()
