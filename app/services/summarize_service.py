import re  # regex  # noqa
import math  # toán  # noqa
import numpy as np  # mảng số  # noqa

from dataclasses import dataclass  # dataclass  # noqa
from typing import Dict, Any, List, Tuple, Set, Optional  # typing  # noqa

import networkx as nx  # TextRank/PageRank  # noqa
from sklearn.feature_extraction.text import TfidfVectorizer  # TF-IDF  # noqa
from sklearn.metrics.pairwise import cosine_similarity  # cosine sim  # noqa


@dataclass
class Sentence:  # câu có metadata paragraph  # noqa
    gid: int  # id câu toàn văn  # noqa
    para_idx: int  # đoạn số mấy  # noqa
    idx_in_para: int  # vị trí trong đoạn  # noqa
    total_in_para: int  # tổng câu trong đoạn  # noqa
    text: str  # nội dung câu  # noqa


@dataclass
class Unit:  # đơn vị ý (mệnh đề/cụm ý)  # noqa
    idx: int  # index unit  # noqa
    text: str  # text unit  # noqa
    sent_gid: int  # thuộc câu gid nào  # noqa
    para_idx: int  # thuộc đoạn nào  # noqa
    sent_in_para: int  # vị trí câu trong đoạn  # noqa
    sent_total_in_para: int  # tổng câu trong đoạn  # noqa
    tokens: List[str]  # token normalized  # noqa
    pos: List[str]  # POS theo token gốc  # noqa
    ner: List[str]  # NER theo token gốc  # noqa
    nps: List[str]  # noun phrases  # noqa


class SummarizeService:
    """
    TÓM TẮT TIẾNG VIỆT (ENSEMBLE) - 1 lần bấm chạy tất cả tiêu chí:
      - Normalize (vá OCR, giữ số thập phân)
      - Split paragraphs -> sentences -> units (mệnh đề)
      - underthesea: tokenize + POS + NER + NP heuristic
      - TF-IDF + centroid similarity
      - TextRank (PageRank) tự code bằng networkx
      - Multi-criteria scoring (A..F)
      - MMR selection (giảm trùng + tăng cover keyphrase)
      - Output: bullet keypoints (gộp theo câu để tránh bullet bị cụt)
    """

    # ====== Config mặc định (bạn có thể chỉnh) ======
    MIN_BULLETS = 3  # tối thiểu 3 ý  # noqa
    RATIO = 0.30  # ~30%  # noqa
    MAX_BULLETS = 12  # chặn quá dài  # noqa

    # ---------- Public API (route gọi y như cũ) ----------
    def summarize(self, text: str, algo: str = "auto", debug: bool = False) -> Dict[str, Any]:
        _ = algo  # ignore algo, luôn ensemble  # noqa

        text = self._normalize(text)  # chuẩn hoá  # noqa
        if not text:  # nếu rỗng  # noqa
            return {"success": False, "error": "EMPTY_TEXT", "error_code": "EMPTY_TEXT"}  # noqa

        sentences = self._split_sentences_with_paragraphs(text)  # tách câu + meta đoạn  # noqa
        if len(sentences) <= 1 and len(sentences[0].text) < 120:  # text quá ngắn  # noqa
            return {"success": True, "algo": "ensemble_vi", "result": sentences[0].text.strip()}  # noqa

        raw_units = self._split_units(sentences)  # tách "ý" (mệnh đề)  # noqa
        units = self._annotate_units(raw_units)  # tokenize + POS + NER + NP  # noqa

        if len(units) <= 1:  # nếu chỉ có 1 ý  # noqa
            only = units[0].text if units else text  # fallback  # noqa
            return {"success": True, "algo": "ensemble_vi", "result": only.strip()}  # noqa

        vec, tfidf, sim = self._tfidf_and_sim(units)  # TF-IDF + sim NxN  # noqa
        tr_scores = self._textrank(sim)  # TextRank score  # noqa
        keyphrases = self._keyphrases(units, vec, tfidf, top_k=25)  # keyphrase toàn đoạn  # noqa
        rows = self._score_all(units, sentences, tfidf, tr_scores, keyphrases)  # chấm điểm tổng  # noqa

        picked_unit_indexes = self._select_mmr(units, rows, sim, keyphrases, sentences)  # chọn bằng MMR  # noqa

        bullets = self._build_bullets(units, picked_unit_indexes)  # build output bullet  # noqa
        result = "\n".join(bullets).strip()  # join bullet  # noqa

        out: Dict[str, Any] = {"success": True, "algo": "ensemble_vi", "result": result if result else text}  # noqa
        if debug:  # nếu bật debug  # noqa
            out["debug"] = {  # debug payload  # noqa
                "note": "always ensemble_vi (algo ignored)",  # noqa
                "sentences": [s.text for s in sentences],  # noqa
                "units": [u.text for u in units],  # noqa
                "keyphrases": keyphrases,  # noqa
                "scores": rows,  # noqa
                "picked_unit_indexes": picked_unit_indexes,  # noqa
            }  # noqa
        return out  # noqa

    # =========================
    # Step 0: Normalize + Split
    # =========================
    def _normalize(self, text: str) -> str:
        text = (text or "").strip()  # trim  # noqa
        text = re.sub(r"\r\n|\r", "\n", text)  # normalize newline  # noqa

        # Vá OCR: "blue-\nchips" -> "blue-chips" (giữ dấu - đúng)  # noqa
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1-\2", text)  # noqa

        # Gộp newline đơn lẻ -> space (OCR hay xuống dòng giữa câu)  # noqa
        # Giữ double newline để còn paragraph boundary  # noqa
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # noqa

        # Chuẩn hoá khoảng trắng  # noqa
        text = re.sub(r"[ \t]+", " ", text)  # noqa
        text = re.sub(r"\n{3,}", "\n\n", text)  # noqa
        return text.strip()  # noqa

    def _split_sentences_with_paragraphs(self, text: str) -> List[Sentence]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p and p.strip()]  # tách đoạn  # noqa
        all_sentences: List[Sentence] = []  # list kết quả  # noqa
        gid = 0  # global sentence id  # noqa

        for pi, para in enumerate(paragraphs):  # duyệt từng đoạn  # noqa
            # tách câu trong đoạn: ., !, ?, ;  # noqa
            parts = re.split(r"(?<=[\.\!\?\;])\s+", para.strip())  # noqa
            parts = [x.strip() for x in parts if x and x.strip()]  # noqa
            total = max(1, len(parts))  # tổng câu trong đoạn  # noqa

            for si, s in enumerate(parts):  # duyệt từng câu  # noqa
                all_sentences.append(Sentence(  # add sentence obj  # noqa
                    gid=gid,  # id câu toàn văn  # noqa
                    para_idx=pi,  # đoạn  # noqa
                    idx_in_para=si,  # vị trí trong đoạn  # noqa
                    total_in_para=total,  # tổng câu trong đoạn  # noqa
                    text=s  # nội dung  # noqa
                ))  # noqa
                gid += 1  # tăng global id  # noqa

        # fallback nếu text không có paragraph/câu rõ  # noqa
        if not all_sentences:  # noqa
            all_sentences = [Sentence(gid=0, para_idx=0, idx_in_para=0, total_in_para=1, text=text.strip())]  # noqa
        return all_sentences  # noqa

    # =========================
    # Step 1: Split units (ý)
    # =========================
    def _split_units(self, sentences: List[Sentence]) -> List[Tuple[Sentence, str]]:
        """
        Tách ý an toàn:
        - Tách theo ';' ':' và ',' nhưng KHÔNG tách khi ',' nằm giữa 2 chữ số (3,62).
        - Không tách theo '-' để tránh phá VN-Index / blue-chips.
        - Nếu chunk quá dài, tách thêm theo marker (lookahead giữ marker).
        """
        punct_split = re.compile(r"(?<!\d),(?!\d)|[;:]", flags=re.IGNORECASE)  # phẩy không kẹp số  # noqa
        marker_split = re.compile(  # marker diễn ngôn mạnh  # noqa
            r"(?=\b(?:nhưng|tuy nhiên|do đó|vì vậy|từ đó|dẫn đến|ngoài ra|đồng thời|mặt khác)\b)",  # noqa
            flags=re.IGNORECASE  # noqa
        )  # noqa

        out: List[Tuple[Sentence, str]] = []  # kết quả raw units  # noqa

        for s in sentences:  # duyệt từng câu  # noqa
            st = (s.text or "").strip()  # text câu  # noqa
            if not st:  # skip rỗng  # noqa
                continue  # noqa

            chunks = [c.strip() for c in punct_split.split(st) if c and c.strip()]  # split punctuation  # noqa
            if len(chunks) <= 1:  # không split được  # noqa
                out.append((s, st))  # giữ nguyên câu  # noqa
                continue  # noqa

            for c in chunks:  # duyệt chunk  # noqa
                if len(c) > 220:  # quá dài -> split thêm marker  # noqa
                    subs = [x.strip() for x in marker_split.split(c) if x and x.strip()]  # noqa
                else:
                    subs = [c]  # giữ 1  # noqa

                for u in subs:  # duyệt unit  # noqa
                    if len(u) < 20:  # quá ngắn -> bỏ (tránh rác kiểu "3,62%")  # noqa
                        continue  # noqa
                    out.append((s, u))  # add unit  # noqa

        if not out:  # fallback nếu split fail  # noqa
            out = [(sentences[0], sentences[0].text.strip())]  # noqa
        return out  # noqa

    # =========================
    # Step 2: VN NLP annotate
    # =========================
    def _annotate_units(self, raw_units: List[Tuple[Sentence, str]]) -> List[Unit]:
        units: List[Unit] = []  # list units  # noqa

        try:  # import underthesea mềm  # noqa
            from underthesea import word_tokenize, pos_tag, ner  # noqa
            has_underthesea = True  # noqa
        except Exception:
            has_underthesea = False  # noqa

        for idx, (sent, utext) in enumerate(raw_units):  # duyệt raw units  # noqa
            utext = (utext or "").strip()  # trim  # noqa
            if not utext:  # skip rỗng  # noqa
                continue  # noqa

            if has_underthesea:  # nếu có underthesea  # noqa
                tok_text = word_tokenize(utext, format="text")  # tokenize (string)  # noqa
                raw_tokens = tok_text.split()  # list token  # noqa

                # POS tag  # noqa
                try:
                    pos_pairs = pos_tag(utext)  # list (token,pos)  # noqa
                except Exception:
                    pos_pairs = []  # noqa
                pos_map: Dict[str, str] = {}  # map token->pos  # noqa
                for item in pos_pairs:  # parse pos tuples  # noqa
                    if isinstance(item, (list, tuple)) and len(item) >= 2:  # đủ cột  # noqa
                        pos_map[str(item[0])] = str(item[1])  # pos nằm cột 2  # noqa

                # NER tag (underthesea có thể trả tuple 2 hoặc 4 cột)  # noqa
                try:
                    ner_pairs = ner(utext)  # noqa
                except Exception:
                    ner_pairs = []  # noqa
                ner_map: Dict[str, str] = {}  # map token->ner  # noqa
                for item in ner_pairs:  # parse ner tuples  # noqa
                    if isinstance(item, (list, tuple)) and len(item) >= 2:  # >=2 cột  # noqa
                        ner_map[str(item[0])] = str(item[1])  # tag ở cột thứ 2  # noqa

                # normalize tokens + stopwords  # noqa
                tokens_norm = [self._norm_token(t) for t in raw_tokens if t and t.strip()]  # noqa
                tokens_norm = [t for t in tokens_norm if t and not self._is_stop_token(t)]  # filter stop  # noqa

                pos_list = [pos_map.get(t, "X") for t in raw_tokens]  # align pos theo token gốc  # noqa
                ner_list = [ner_map.get(t, "O") for t in raw_tokens]  # align ner theo token gốc  # noqa
                nps = self._np_phrases(raw_tokens, pos_list, ner_list)  # NP heuristic  # noqa
            else:
                raw_tokens = re.findall(r"[0-9A-Za-zÀ-ỹà-ỹ]+", utext)  # fallback token  # noqa
                tokens_norm = [self._norm_token(t) for t in raw_tokens]  # lower  # noqa
                tokens_norm = [t for t in tokens_norm if t and not self._is_stop_token(t)]  # stop  # noqa
                pos_list = ["X"] * len(raw_tokens)  # noqa
                ner_list = ["O"] * len(raw_tokens)  # noqa
                nps = []  # noqa

            units.append(Unit(  # build unit  # noqa
                idx=idx,  # unit idx  # noqa
                text=utext,  # text  # noqa
                sent_gid=sent.gid,  # câu gid  # noqa
                para_idx=sent.para_idx,  # đoạn  # noqa
                sent_in_para=sent.idx_in_para,  # vị trí câu trong đoạn  # noqa
                sent_total_in_para=sent.total_in_para,  # tổng câu trong đoạn  # noqa
                tokens=tokens_norm,  # tokens  # noqa
                pos=pos_list,  # pos  # noqa
                ner=ner_list,  # ner  # noqa
                nps=nps  # noun phrases  # noqa
            ))  # noqa

        return units  # noqa

    def _norm_token(self, t: str) -> str:
        return (t or "").strip().lower()  # normalize token  # noqa

    def _vn_stopwords(self) -> Set[str]:
        return {  # stopwords VN cơ bản  # noqa
            "và", "hoặc", "nhưng", "trong", "trên", "tại", "đến", "cho", "của", "với", "bởi", "từ", "là",
            "đã", "đang", "sẽ", "có", "không", "một", "những", "các", "này", "đó", "vậy", "thì", "khi", "nếu",
            "vì", "do", "rằng", "được", "nên", "cũng", "như", "vừa", "rất", "hơn", "kém", "nữa", "ra", "vào",
            "để", "nhằm", "theo", "lên", "xuống", "giữa", "vẫn", "còn", "lại", "đều", "đang", "sau", "trước"
        }  # noqa

    def _is_stop_token(self, t: str) -> bool:
        if not t:  # rỗng  # noqa
            return True  # noqa
        if t in self._vn_stopwords():  # stopword  # noqa
            return True  # noqa
        # giữ số / % / thập phân => không coi là stop  # noqa
        if re.fullmatch(r"\d+(?:[.,]\d+)?%?", t):  # number pattern  # noqa
            return False  # noqa
        if len(t) <= 1:  # token quá ngắn  # noqa
            return True  # noqa
        return False  # noqa

    def _np_phrases(self, tokens: List[str], pos: List[str], ner: List[str]) -> List[str]:
        out: List[str] = []  # output NP  # noqa
        buf: List[str] = []  # buffer  # noqa

        def flush():  # đẩy buffer ra  # noqa
            if len(buf) >= 2:  # NP đủ dài  # noqa
                out.append(" ".join(buf))  # join NP  # noqa
            buf.clear()  # reset  # noqa

        for w, p, n in zip(tokens, pos, ner):  # duyệt token  # noqa
            if n and n != "O":  # entity token  # noqa
                flush()  # flush trước  # noqa
                out.append(w)  # giữ entity như phrase  # noqa
                continue  # noqa

            p = (p or "").upper()  # normalize POS  # noqa
            if p.startswith("N") or p.startswith("A"):  # noun/adj  # noqa
                buf.append(w)  # add token  # noqa
            else:
                flush()  # kết thúc NP  # noqa

        flush()  # flush cuối  # noqa

        # unique hoá  # noqa
        seen: Set[str] = set()  # noqa
        final: List[str] = []  # noqa
        for x in out:  # duyệt phrase  # noqa
            k = x.lower().strip()  # normalize  # noqa
            if not k or k in seen:  # skip trùng  # noqa
                continue  # noqa
            seen.add(k)  # mark seen  # noqa
            final.append(x.strip())  # add  # noqa
        return final  # noqa

    # =========================
    # Step 3: TF-IDF + Similarity
    # =========================
    def _tfidf_and_sim(self, units: List[Unit]):
        docs = [" ".join(u.tokens) for u in units]  # unit -> doc  # noqa
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)  # 1-2gram  # noqa
        tfidf = vec.fit_transform(docs)  # sparse  # noqa
        sim = cosine_similarity(tfidf)  # NxN  # noqa
        return vec, tfidf, sim  # noqa

    # =========================
    # Step 4: TextRank (networkx)
    # =========================
    def _textrank(self, sim) -> Dict[int, float]:
        n = int(sim.shape[0])  # số node  # noqa
        g = nx.Graph()  # graph  # noqa
        g.add_nodes_from(range(n))  # add nodes  # noqa

        thr = 0.10  # threshold cạnh  # noqa
        for i in range(n):  # duyệt i  # noqa
            for j in range(i + 1, n):  # duyệt j  # noqa
                w = float(sim[i, j])  # weight  # noqa
                if w >= thr:  # đủ liên quan  # noqa
                    g.add_edge(i, j, weight=w)  # add edge  # noqa

        if g.number_of_edges() == 0:  # graph rỗng cạnh  # noqa
            return {i: 1.0 / max(1, n) for i in range(n)}  # đều nhau  # noqa

        pr = nx.pagerank(g, alpha=0.85, weight="weight")  # PageRank  # noqa
        mx = max(pr.values()) if pr else 1.0  # max để normalize  # noqa
        return {i: (pr.get(i, 0.0) / mx if mx > 0 else 0.0) for i in range(n)}  # 0..1  # noqa

    # =========================
    # Keyphrases
    # =========================
    def _keyphrases(self, units: List[Unit], vec: TfidfVectorizer, tfidf, top_k: int = 25) -> List[str]:
        phrases: List[str] = []  # danh sách phrase  # noqa

        # 1) NP  # noqa
        for u in units:  # noqa
            phrases.extend(u.nps)  # noqa

        # 2) Entity token  # noqa
        for u in units:  # noqa
            for w, t in zip(u.tokens, u.ner):  # noqa
                if t and t != "O":  # noqa
                    phrases.append(w)  # noqa

        # 3) Top TF-IDF terms toàn đoạn  # noqa
        try:
            feature_names = vec.get_feature_names_out()  # vocab  # noqa
            centroid = tfidf.sum(axis=0)  # sum vector  # noqa
            centroid = np.asarray(centroid).ravel()  # -> ndarray 1D  # noqa
            top_idx = centroid.argsort()[::-1][:top_k]  # top indices  # noqa
            for i in top_idx:  # noqa
                if centroid[i] > 0:  # noqa
                    phrases.append(str(feature_names[i]))  # noqa
        except Exception:
            pass  # ignore  # noqa

        # unique + lọc rác  # noqa
        seen: Set[str] = set()  # noqa
        out: List[str] = []  # noqa
        for p in phrases:  # noqa
            p = (p or "").strip().lower()  # noqa
            if len(p) < 2:  # noqa
                continue  # noqa
            if p in seen:  # noqa
                continue  # noqa
            seen.add(p)  # noqa
            out.append(p)  # noqa

        return out[:top_k]  # noqa

    # =========================
    # Multi-criteria scoring
    # =========================
    def _score_all(
        self,
        units: List[Unit],
        sentences: List[Sentence],
        tfidf,
        tr_scores: Dict[int, float],
        keyphrases: List[str]
    ) -> List[Dict[str, Any]]:
        keyset = set(keyphrases)  # keyphrase set  # noqa
        total_sents = max(1, len(sentences))  # tổng câu  # noqa

        cue = [  # marker kết luận/nhấn mạnh  # noqa
            "tóm lại", "kết luận", "nhìn chung", "tổng quan", "nói chung",
            "do đó", "vì vậy", "từ đó", "dẫn đến",
            "mục tiêu", "nhằm", "để",
            "đề xuất", "giải pháp", "khuyến nghị", "cần", "nên"
        ]  # noqa

        actions = [  # câu hành động kiểu email  # noqa
            "cần", "yêu cầu", "đề nghị", "thực hiện", "triển khai", "kiểm tra",
            "cập nhật", "gửi", "xác nhận", "hoàn thành", "báo cáo", "nộp"
        ]  # noqa

        time_words = [  # mốc thời gian/ràng buộc  # noqa
            "trước", "trong vòng", "hạn", "deadline", "ngày", "tuần này", "tháng", "giờ", "phút"
        ]  # noqa

        # centroid vector (fix np.matrix)  # noqa
        centroid_vec = tfidf.mean(axis=0)  # mean vector  # noqa
        centroid_vec = np.asarray(centroid_vec)  # convert to ndarray (fix sklearn error)  # noqa
        centroid_vec = centroid_vec.reshape(1, -1) if centroid_vec.ndim == 2 else centroid_vec.reshape(1, -1)  # 2D  # noqa
        centroid_sim = cosine_similarity(tfidf, centroid_vec)  # Nx1  # noqa

        rows: List[Dict[str, Any]] = []  # output rows  # noqa

        for i, u in enumerate(units):  # duyệt unit  # noqa
            text_low = u.text.lower()  # text lower  # noqa
            token_str = " ".join(u.tokens)  # token string để match keyphrase  # noqa

            # A1/A2 theo đoạn: câu chủ đề (1-2 câu đầu đoạn) / câu kết (1-2 câu cuối đoạn)  # noqa
            topic_boost = 1.0 if u.sent_in_para <= 1 else 0.0  # topic  # noqa
            concl_boost = 1.0 if u.sent_in_para >= max(0, u.sent_total_in_para - 2) else 0.0  # concl  # noqa

            # thêm nhẹ theo toàn văn: 1-2 câu đầu/cuối document  # noqa
            doc_topic = 1.0 if u.sent_gid <= 1 else 0.0  # đầu văn  # noqa
            doc_concl = 1.0 if u.sent_gid >= max(0, total_sents - 2) else 0.0  # cuối văn  # noqa

            # A3 cue markers  # noqa
            cue_hit = 1.0 if any(c in text_low for c in cue) else 0.0  # noqa

            # B1 actionability  # noqa
            action_hit = 1.0 if any(a in text_low for a in actions) else 0.0  # noqa

            # B2 deadline/time  # noqa
            has_timeword = any(t in text_low for t in time_words)  # noqa
            has_date_like = bool(re.search(r"\b\d{1,2}[\/\-]\d{1,2}([\/\-]\d{2,4})?\b", text_low))  # noqa
            deadline_hit = 1.0 if (has_timeword or has_date_like) else 0.0  # noqa

            # C1 keyphrase overlap (match theo tokens để không lệch do underthesea dùng _)  # noqa
            kp_hit = 0  # counter  # noqa
            for kp in keyset:  # noqa
                if kp in token_str:  # noqa
                    kp_hit += 1  # noqa
            kp_score = kp_hit / max(1, len(keyset))  # normalize  # noqa

            # C2 centroid similarity  # noqa
            c2 = float(centroid_sim[i, 0])  # noqa

            # C3 TextRank  # noqa
            c3 = float(tr_scores.get(i, 0.0))  # noqa

            # D1 NP density  # noqa
            np_density = min(1.0, len(u.nps) / 3.0)  # noqa

            # D2 POS weight  # noqa
            pos_score = self._pos_weight(u.pos)  # noqa

            # D3 NER bonus  # noqa
            ner_count = sum(1 for t in u.ner if t and t != "O")  # noqa
            ner_score = min(1.0, ner_count / 2.0)  # noqa

            # E1 numeric (giữ số thập phân, %, điểm)  # noqa
            numeric = 1.0 if re.search(r"\d", text_low) else 0.0  # noqa

            # E2 length normalization  # noqa
            length_score = self._length_score(len(u.tokens))  # noqa

            # Weights tổng hợp (bạn có thể tinh chỉnh)  # noqa
            W = {  # noqa
                "topic": 0.9,  # đoạn đầu  # noqa
                "concl": 0.7,  # đoạn cuối  # noqa
                "doc_topic": 0.3,  # đầu văn  # noqa
                "doc_concl": 0.3,  # cuối văn  # noqa
                "cue": 0.7,  # marker  # noqa
                "action": 0.8,  # email/action  # noqa
                "deadline": 0.7,  # deadline  # noqa
                "kp": 1.0,  # keyphrase  # noqa
                "centroid": 1.0,  # centroid  # noqa
                "textrank": 1.0,  # graph centrality  # noqa
                "np": 0.8,  # noun phrase density  # noqa
                "pos": 0.6,  # POS  # noqa
                "ner": 0.7,  # entity  # noqa
                "num": 0.6,  # số liệu  # noqa
                "len": 0.6,  # độ dài hợp lý  # noqa
            }  # noqa

            total = (  # tổng điểm  # noqa
                W["topic"] * topic_boost +  # noqa
                W["concl"] * concl_boost +  # noqa
                W["doc_topic"] * doc_topic +  # noqa
                W["doc_concl"] * doc_concl +  # noqa
                W["cue"] * cue_hit +  # noqa
                W["action"] * action_hit +  # noqa
                W["deadline"] * deadline_hit +  # noqa
                W["kp"] * kp_score +  # noqa
                W["centroid"] * c2 +  # noqa
                W["textrank"] * c3 +  # noqa
                W["np"] * np_density +  # noqa
                W["pos"] * pos_score +  # noqa
                W["ner"] * ner_score +  # noqa
                W["num"] * numeric +  # noqa
                W["len"] * length_score  # noqa
            )  # noqa

            rows.append({  # lưu row  # noqa
                "idx": i,  # unit index  # noqa
                "total": float(total),  # raw total  # noqa
                "signals": {  # debug signals  # noqa
                    "topic": topic_boost,  # noqa
                    "concl": concl_boost,  # noqa
                    "doc_topic": doc_topic,  # noqa
                    "doc_concl": doc_concl,  # noqa
                    "cue": cue_hit,  # noqa
                    "action": action_hit,  # noqa
                    "deadline": deadline_hit,  # noqa
                    "kp": kp_score,  # noqa
                    "centroid": c2,  # noqa
                    "textrank": c3,  # noqa
                    "np": np_density,  # noqa
                    "pos": pos_score,  # noqa
                    "ner": ner_score,  # noqa
                    "num": numeric,  # noqa
                    "len": length_score,  # noqa
                }  # noqa
            })  # noqa

        return rows  # noqa

    def _pos_weight(self, pos_tags: List[str]) -> float:
        if not pos_tags:  # noqa
            return 0.0  # noqa
        score = 0.0  # noqa
        for p in pos_tags:  # noqa
            p = (p or "").upper()  # noqa
            if p.startswith("N"):  # noun  # noqa
                score += 1.0  # noqa
            elif p.startswith("V"):  # verb  # noqa
                score += 0.7  # noqa
            elif p.startswith("A"):  # adj  # noqa
                score += 0.5  # noqa
            else:
                score += 0.1  # noqa
        return min(1.0, score / max(1, len(pos_tags)))  # noqa

    def _length_score(self, n_tokens: int) -> float:
        if n_tokens <= 0:  # noqa
            return 0.0  # noqa
        if 8 <= n_tokens <= 28:  # noqa
            return 1.0  # noqa
        if n_tokens < 8:  # noqa
            return n_tokens / 8.0  # noqa
        return max(0.0, 1.0 - (n_tokens - 28) / 28.0)  # noqa

    # =========================
    # MMR selection (proper loop)
    # =========================
    def _select_mmr(
        self,
        units: List[Unit],
        rows: List[Dict[str, Any]],
        sim,
        keyphrases: List[str],
        sentences: List[Sentence]
    ) -> List[int]:
        n_units = len(units)  # số unit  # noqa
        n_sents = max(1, len(sentences))  # số câu  # noqa

        target = max(self.MIN_BULLETS, math.ceil(n_sents * self.RATIO))  # >=3, ~30% theo câu  # noqa
        target = min(self.MAX_BULLETS, target)  # cap  # noqa

        scores = np.array([float(r["total"]) for r in rows], dtype=float)  # base scores  # noqa
        mx = float(scores.max()) if scores.size else 1.0  # max  # noqa
        if mx > 0:  # normalize 0..1  # noqa
            scores = scores / mx  # noqa

        keyset = set(keyphrases)  # set keyphrase  # noqa

        picked: List[int] = []  # list picked unit index  # noqa
        covered: Set[str] = set()  # keyphrase covered  # noqa

        lam = 0.70  # ưu tiên chất lượng  # noqa
        beta = 0.60  # phạt redundancy  # noqa
        hard_skip = 0.85  # quá trùng thì skip  # noqa

        candidate_set = set(range(n_units))  # all candidates  # noqa

        for _k in range(target):  # chọn từng bước  # noqa
            best_i: Optional[int] = None  # best candidate  # noqa
            best_val = -1e9  # best mmr score  # noqa

            for i in list(candidate_set):  # duyệt candidate  # noqa
                base = float(scores[i])  # base score normalized  # noqa

                red = 0.0  # redundancy  # noqa
                if picked:  # nếu đã chọn  # noqa
                    red = max(float(sim[i, j]) for j in picked)  # max sim  # noqa
                if red >= hard_skip:  # quá trùng  # noqa
                    continue  # noqa

                token_str = " ".join(units[i].tokens)  # token string  # noqa
                new_kp = 0  # count new keyphrase  # noqa
                for kp in keyset:  # noqa
                    if kp in token_str and kp not in covered:  # noqa
                        new_kp += 1  # noqa
                cov = min(1.0, new_kp / 3.0)  # normalize coverage  # noqa

                mmr = lam * base + (1 - lam) * cov - beta * red  # mmr formula  # noqa

                if mmr > best_val:  # update best  # noqa
                    best_val = mmr  # noqa
                    best_i = i  # noqa

            if best_i is None:  # không còn candidate hợp lệ  # noqa
                break  # noqa

            picked.append(best_i)  # accept  # noqa
            candidate_set.remove(best_i)  # remove  # noqa

            token_str = " ".join(units[best_i].tokens)  # token str  # noqa
            for kp in keyset:  # update coverage  # noqa
                if kp in token_str:  # noqa
                    covered.add(kp)  # noqa

        # đảm bảo tối thiểu 3 (trường hợp text ngắn/graph thưa)  # noqa
        if len(picked) < self.MIN_BULLETS:  # noqa
            ranked = sorted(range(n_units), key=lambda i: float(scores[i]), reverse=True)  # noqa
            for i in ranked:  # noqa
                if i in picked:  # noqa
                    continue  # noqa
                picked.append(i)  # noqa
                if len(picked) >= self.MIN_BULLETS:  # noqa
                    break  # noqa

        return sorted(set(picked), key=lambda i: (units[i].sent_gid, i))  # sort theo câu  # noqa

    # =========================
    # Output bullets (merge by sentence)
    # =========================
    def _build_bullets(self, units: List[Unit], picked: List[int]) -> List[str]:
        if not picked:  # noqa
            return []  # noqa

        # group theo câu gốc để tránh bullet quá cụt  # noqa
        grouped: Dict[int, List[int]] = {}  # sent_gid -> unit indexes  # noqa
        for i in picked:  # noqa
            sg = units[i].sent_gid  # noqa
            grouped.setdefault(sg, []).append(i)  # noqa

        bullets: List[str] = []  # output bullets  # noqa
        for sg in sorted(grouped.keys()):  # theo thứ tự câu  # noqa
            ids = sorted(grouped[sg])  # theo thứ tự unit  # noqa
            parts = [units[i].text.strip() for i in ids if units[i].text.strip()]  # collect parts  # noqa
            if not parts:  # noqa
                continue  # noqa
            text = ", ".join(parts)  # nối các ý cùng câu  # noqa
            text = re.sub(r"\s+", " ", text).strip()  # clean spaces  # noqa
            bullets.append(f"- {text}")  # add bullet  # noqa

        # nếu merge làm còn < MIN_BULLETS thì fallback: bullet theo unit  # noqa
        if len(bullets) < self.MIN_BULLETS:  # noqa
            bullets = [f"- {units[i].text.strip()}" for i in picked if units[i].text.strip()]  # noqa

        return bullets  # noqa
