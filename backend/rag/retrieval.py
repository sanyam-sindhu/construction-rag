"""Hybrid retrieval: BM25 + dense (multilingual-e5), fused with Reciprocal Rank Fusion.

Why both: the schedule of rates is full of near-duplicate rows that differ only by a
size ("250mm dia" vs "300mm dia") — lexical matching nails those; the Hindi scan is
queried in English — only a multilingual dense model can bridge that. RRF needs no
score calibration between the two.
"""

import hashlib
import re
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from rank_bm25 import BM25Okapi

from .chunk import Chunk, read_chunks
from .config import BASE_EMBED_MODEL, BM25_WEIGHT, CHUNKS_PATH, EMBED_MODEL, FINETUNED_EMBED_DIR, INDEX_DIR

TOKEN_RE = re.compile(r"[a-z]+|\d+(?:\.\d+)*|[ऀ-ॣ०-ॿ]+")
ITEM_CODE_RE = re.compile(r"\b([GBSELHR])\s*-\s*(\d{1,5}(?:\.\d{1,3}){0,4})\b", re.I)
STOP = {"the", "a", "an", "of", "for", "to", "in", "and", "or", "is", "what", "which", "per", "as", "by",
        "with", "on", "at", "be", "shall", "how", "much", "does", "do", "are", "rate", "cost", "price"}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOP]


def resolve_model(name: str = EMBED_MODEL) -> str:
    if name == "finetuned":
        return str(FINETUNED_EMBED_DIR) if FINETUNED_EMBED_DIR.exists() else BASE_EMBED_MODEL
    if name == "base":
        return BASE_EMBED_MODEL
    return name


@lru_cache(maxsize=4)
def load_encoder(path: str):
    from sentence_transformers import SentenceTransformer

    import torch
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    model = SentenceTransformer(path, device=device)
    model.max_seq_length = 512
    return model


def encode_queries(model, queries: list[str]) -> np.ndarray:
    return model.encode([f"query: {q}" for q in queries], normalize_embeddings=True, batch_size=64,
                        convert_to_numpy=True)


def encode_passages(model, texts: list[str], show_progress=False) -> np.ndarray:
    return model.encode([f"passage: {t}" for t in texts], normalize_embeddings=True, batch_size=32,
                        convert_to_numpy=True, show_progress_bar=show_progress)


@dataclass
class Hit:
    chunk: Chunk
    score: float
    bm25_rank: int | None = None
    dense_rank: int | None = None


class Retriever:
    def __init__(self, chunks: list[Chunk] | None = None, model: str = EMBED_MODEL):
        self.chunks = chunks if chunks is not None else read_chunks(CHUNKS_PATH)
        self.by_id = {c.id: i for i, c in enumerate(self.chunks)}
        self.bm25 = BM25Okapi([tokenize(c.text) for c in self.chunks])
        self.doc_ids = np.array([c.doc_id for c in self.chunks])
        self._emb = {}
        self.default_model = model

    # ---- dense -------------------------------------------------------------------------
    def embeddings(self, model_name: str) -> np.ndarray:
        path = resolve_model(model_name)
        if path not in self._emb:
            h = hashlib.md5(path.encode())
            weights = Path(path) / "model.safetensors"
            if weights.exists():  # local model dirs get overwritten (train / interpolate): key on the weights too
                h.update(f"{weights.stat().st_mtime_ns}-{weights.stat().st_size}".encode())
            for c in self.chunks:
                h.update(c.text.encode())
            key = h.hexdigest()[:12]
            cache = INDEX_DIR / f"emb-{key}.npy"
            if cache.exists():
                self._emb[path] = np.load(cache)
            else:
                emb = encode_passages(load_encoder(path), [c.text for c in self.chunks])
                INDEX_DIR.mkdir(parents=True, exist_ok=True)
                np.save(cache, emb)
                self._emb[path] = emb
        return self._emb[path]

    def warm(self, model_name: str | None = None) -> None:
        model_name = model_name or self.default_model
        self.embeddings(model_name)
        encode_queries(load_encoder(resolve_model(model_name)), ["warm-up"])

    def dense_scores(self, query: str, model_name: str) -> np.ndarray:
        path = resolve_model(model_name)
        q = encode_queries(load_encoder(path), [query])[0]
        return self.embeddings(model_name) @ q

    # ---- search ------------------------------------------------------------------------
    def search(self, query: str, k: int = 8, docs: list[str] | None = None, mode: str = "hybrid",
               model: str | None = None, pool: int = 50, bm25_weight: float | None = None) -> list[Hit]:
        model = model or self.default_model
        weights = {"dense": 1.0, "bm25": BM25_WEIGHT if bm25_weight is None else bm25_weight}
        mask = np.isin(self.doc_ids, docs) if docs else np.ones(len(self.chunks), bool)
        ranks: dict[str, list[int]] = {}
        if mode in ("hybrid", "bm25"):
            s = self.bm25.get_scores(tokenize(query))
            s = np.where(mask, s, -np.inf)
            ranks["bm25"] = [i for i in np.argsort(-s)[:pool] if s[i] > 0]
        if mode in ("hybrid", "dense"):
            s = np.where(mask, self.dense_scores(query, model), -np.inf)
            ranks["dense"] = list(np.argsort(-s)[:pool])

        # Weighted RRF. BM25 gets a lower weight: it always returns *something*, and for an
        # English question about the Hindi document everything it returns is noise.
        fused: dict[int, float] = {}
        for name, idxs in ranks.items():
            w = weights[name] if mode == "hybrid" else 1.0
            for r, i in enumerate(idxs):
                fused[i] = fused.get(i, 0.0) + w / (60 + r + 1)

        # Exact BSR item codes ("B-1.5.2", "item S-5.4.1") are unambiguous: pin them first.
        for sec, code in ITEM_CODE_RE.findall(query):
            i = self.by_id.get(f"bsr-{sec.upper()}-{code}")
            if i is not None and mask[i]:
                fused[i] = 1.0

        order = sorted(fused, key=fused.get, reverse=True)[:k]
        pos = {name: {i: r + 1 for r, i in enumerate(idxs)} for name, idxs in ranks.items()}
        return [Hit(self.chunks[i], fused[i], pos.get("bm25", {}).get(i), pos.get("dense", {}).get(i)) for i in order]
