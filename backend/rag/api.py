"""FastAPI app.

    uvicorn rag.api:app --port 8000        (from backend/)

POST /api/ask streams NDJSON: first the retrieved sources, then answer tokens, then
the list of source numbers the answer actually cited.
"""

import json
import time
from collections import Counter
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from .config import DOCS, FINETUNED_EMBED_DIR, PDF_DIR
from .generate import backend_info, cited_numbers, stream_answer
from .retrieval import Hit, Retriever


@asynccontextmanager
async def lifespan(_app):
    retriever()  # load chunks, BM25 and embeddings before the first request
    yield


app = FastAPI(title="Construction RAG", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_retriever: Retriever | None = None


def retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
        _retriever.warm()  # build/load the vector cache and the query encoder up front
    return _retriever


class SearchRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    k: int = Field(6, ge=1, le=20)
    docs: list[str] | None = None
    mode: Literal["hybrid", "bm25", "dense"] = "hybrid"
    model: Literal["finetuned", "base"] = "finetuned"


def hit_json(n: int, h: Hit) -> dict:
    c = h.chunk
    return {"n": n, "id": c.id, "doc_id": c.doc_id, "doc": DOCS[c.doc_id]["short"], "ref": c.ref,
            "section": c.section, "page": c.page, "page_label": c.page_label, "lang": c.lang,
            "text": c.text, "score": round(h.score, 4), "bm25_rank": h.bm25_rank, "dense_rank": h.dense_rank,
            "boxes": c.meta.get("boxes", {})}


@app.get("/api/health")
def health():
    r = retriever()
    return {"chunks": len(r.chunks), "llm": backend_info(),
            "embedder": {"default": r.default_model, "finetuned_available": FINETUNED_EMBED_DIR.exists()}}


@app.get("/api/documents")
def documents():
    counts = Counter(c.doc_id for c in retriever().chunks)
    return [{"id": k, **v, "chunks": counts.get(k, 0)} for k, v in DOCS.items()]


@app.post("/api/search")
def search(req: SearchRequest):
    t = time.time()
    hits = retriever().search(req.question, k=req.k, docs=req.docs, mode=req.mode, model=req.model)
    return {"hits": [hit_json(n, h) for n, h in enumerate(hits, 1)], "ms": round(1000 * (time.time() - t))}


@app.post("/api/ask")
def ask(req: SearchRequest):
    t = time.time()
    hits = retriever().search(req.question, k=req.k, docs=req.docs, mode=req.mode, model=req.model)
    retrieval_ms = round(1000 * (time.time() - t))

    def events():
        yield json.dumps({"type": "sources", "sources": [hit_json(n, h) for n, h in enumerate(hits, 1)],
                          "retrieval_ms": retrieval_ms, "llm": backend_info()}) + "\n"
        answer = []
        try:
            for tok in stream_answer(req.question, hits):
                answer.append(tok)
                yield json.dumps({"type": "token", "text": tok}) + "\n"
        except Exception as e:  # surface LLM/backend errors to the UI instead of a dead stream
            yield json.dumps({"type": "error", "message": f"{type(e).__name__}: {e}"}) + "\n"
        yield json.dumps({"type": "done", "cited": cited_numbers("".join(answer), len(hits)),
                          "total_ms": round(1000 * (time.time() - t))}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


@app.get("/api/page/{doc_id}/{page}.png")
def page_image(doc_id: str, page: int, chunk: str | None = None, dpi: int = 110):
    """Render one PDF page, with the cited chunk's region highlighted."""
    import pymupdf

    if doc_id not in DOCS:
        raise HTTPException(404, "unknown document")
    doc = pymupdf.open(PDF_DIR / DOCS[doc_id]["file"])
    if not 1 <= page <= doc.page_count:
        raise HTTPException(404, "page out of range")
    pg = doc[page - 1]
    r = retriever()
    if chunk and chunk in r.by_id:
        for x0, y0, x1, y1 in r.chunks[r.by_id[chunk]].meta.get("boxes", {}).get(str(page), []):
            rect = pymupdf.Rect(x0 - 3, y0 - 2, x1 + 3, y1 + 2) * pg.derotation_matrix
            pg.draw_rect(rect, color=(0.92, 0.45, 0.05), fill=(1.0, 0.8, 0.2), fill_opacity=0.28, width=1.2, overlay=True)
    png = pg.get_pixmap(dpi=min(max(dpi, 60), 200)).tobytes("png")
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=3600"})


@app.get("/api/pdf/{doc_id}")
def pdf(doc_id: str):
    if doc_id not in DOCS:
        raise HTTPException(404, "unknown document")
    path = PDF_DIR / DOCS[doc_id]["file"]
    if not path.exists():
        raise HTTPException(404, f"{path.name} not found in {PDF_DIR}")
    return FileResponse(path, media_type="application/pdf", content_disposition_type="inline")
