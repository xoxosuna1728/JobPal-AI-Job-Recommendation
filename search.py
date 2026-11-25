"""Hybrid job search: SQL filters first, then semantic ranking by embedding similarity.

Uses sentence-transformers embeddings. If that library or model is unavailable
(for example no internet), it falls back to TF-IDF so the project still runs.
"""
import os

from db import query

MODEL_NAME = os.getenv("JOBPAL_EMBED_MODEL", "all-MiniLM-L6-v2")


class JobIndex:
    def __init__(self):
        rows = query("SELECT * FROM jobs ORDER BY id")
        self.ids = [r["id"] for r in rows]
        self.pos = {job_id: i for i, job_id in enumerate(self.ids)}
        texts = [f"{r['title']} at {r['company']}. Skills: {r['skills']}. {r['description']}" for r in rows]
        self._build(texts)

    def _build(self, texts):
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(MODEL_NAME)
            self.matrix = model.encode(texts, normalize_embeddings=True)
            self._encode = lambda q: model.encode([q], normalize_embeddings=True)[0]
            self.backend = "embeddings"
        except Exception as exc:  # noqa: BLE001
            print(f"[search] embeddings unavailable ({exc.__class__.__name__}); using TF-IDF fallback")
            from sklearn.feature_extraction.text import TfidfVectorizer

            vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.matrix = vec.fit_transform(texts).toarray()
            self._encode = lambda q: vec.transform([q]).toarray()[0]
            self.backend = "tfidf"

    def search(self, query_text, top_k=5, location=None, job_type=None, work_mode=None, min_pay=None):
        where, params = [], []
        if location:
            where.append("LOWER(location) LIKE ?")
            params.append(f"%{location.lower()}%")
        if job_type:
            where.append("job_type = ?")
            params.append(job_type)
        if work_mode:
            where.append("work_mode = ?")
            params.append(work_mode)
        if min_pay:
            where.append("pay_per_month >= ?")
            params.append(int(min_pay))

        sql = "SELECT * FROM jobs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        candidates = query(sql, params)
        if not candidates:
            return []

        qv = self._encode(query_text)
        scored = sorted(
            ((float(self.matrix[self.pos[r["id"]]] @ qv), r) for r in candidates),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "company": r["company"],
                "location": r["location"],
                "work_mode": r["work_mode"],
                "job_type": r["job_type"],
                "pay_per_month": r["pay_per_month"],
                "skills": r["skills"],
                "score": round(score, 3),
            }
            for score, r in scored[:top_k]
        ]
