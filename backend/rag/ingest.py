"""Parse the three PDFs into citation-ready chunks → data/processed/chunks.jsonl.

    python -m rag.ingest

OCR results are cached in data/processed/ocr/*.json, so Tesseract is only needed
the first time (the cache is committed, so usually not at all).
"""

import collections
import time

from .chunk import write_chunks
from .config import CHUNKS_PATH, DOCS, PDF_DIR
from .parsers import bsr, is456, pmgsy

PARSERS = {"is456": is456.parse, "bsr": bsr.parse, "pmgsy": pmgsy.parse}


def main():
    all_chunks = []
    for doc_id, parse in PARSERS.items():
        path = PDF_DIR / DOCS[doc_id]["file"]
        t = time.time()
        chunks = parse(path)
        types = collections.Counter(c.meta.get("type") for c in chunks)
        print(f"{doc_id:6s} {len(chunks):6d} chunks  {dict(types)}  ({time.time() - t:.1f}s)")
        all_chunks.extend(chunks)
    ids = [c.id for c in all_chunks]
    assert len(ids) == len(set(ids)), "duplicate chunk ids"
    write_chunks(all_chunks, CHUNKS_PATH)
    print(f"wrote {len(all_chunks)} chunks → {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
