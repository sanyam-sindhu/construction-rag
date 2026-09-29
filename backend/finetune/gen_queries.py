"""Generate synthetic training queries for embedding fine-tuning with a local LLM.

    python -m finetune.gen_queries [--limit-bsr 150] [--workers 4]

For each sampled chunk the LLM writes questions a practitioner would ask that the
chunk answers (InPars / Promptagator-style). Output: data/finetune/queries.jsonl,
one {"chunk_id", "query", "lang"} per line. Resumable: already-done chunks are skipped.
The generated file is committed, so reproducing training does not require an LLM.
"""

import argparse
import json
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

from rag.chunk import read_chunks
from rag.config import CHUNKS_PATH, DATA_DIR, LLM_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL

OUT = DATA_DIR / "finetune" / "queries.jsonl"

EN_PROMPT = """You write search queries that a civil engineer, estimator or contractor in India would type to find the passage below in a large collection of construction documents.

Passage (from {section}):
\"\"\"{text}\"\"\"

Write {n} diverse, natural questions that this passage answers. Rules:
- Paraphrase; do not copy long phrases. Mix styles: a full question, a short keyword-style query, a practical on-site scenario.
- Include the details that distinguish this passage from similar ones (sizes, diameters, grades, depths, materials).
- Never mention item numbers, clause numbers, page numbers, or say "this passage/document/schedule".
- Output JSON only: {{"questions": [...]}}"""

HI_PROMPT = """You write search queries that an engineer or official working on rural roads in India would ask about the passage below (Hindi text, OCR'd from the PMGSY guidelines).

Passage (from {section}):
\"\"\"{text}\"\"\"

Write 3 diverse, natural questions that this passage answers: 2 in English and 1 in Hindi (Devanagari).
Rules: paraphrase, be specific to this passage, never mention paragraph or page numbers or say "this passage".
Output JSON only: {{"questions": [{{"lang": "en", "q": "..."}}, {{"lang": "en", "q": "..."}}, {{"lang": "hi", "q": "..."}}]}}"""


def ask(client, prompt):
    r = client.post(f"{OPENAI_BASE_URL}/chat/completions", json={
        "model": LLM_MODEL, "temperature": 0.7, "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}]},
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}, timeout=180)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    content = re.sub(r"^```(json)?|```$", "", content.strip()).strip()
    return json.loads(content)["questions"]


def select_chunks(limit_bsr, seed=13):
    chunks = read_chunks(CHUNKS_PATH)
    rng = random.Random(seed)
    is456 = [c for c in chunks if c.doc_id == "is456"]
    pmgsy = [c for c in chunks if c.doc_id == "pmgsy" and len(c.text.split()) > 25]
    items = [c for c in chunks if c.doc_id == "bsr" and c.meta.get("type") == "item" and c.meta.get("rate")]
    # Stratify BSR by section so small sections (Lift, Horticulture, Road) are represented.
    by_sec = {}
    for c in items:
        by_sec.setdefault(c.id.split("-")[1], []).append(c)
    share = {s: max(10, int(limit_bsr * len(v) / len(items))) for s, v in by_sec.items()}
    bsr = [c for s, v in by_sec.items() for c in rng.sample(v, min(len(v), share[s]))]
    # PMGSY first: cross-lingual (English → Hindi) queries are what the base model lacks most.
    return pmgsy + is456 + bsr


def job(client, c):
    text = " ".join(c.text.split()[:350])
    if c.doc_id == "pmgsy":
        qs = ask(client, HI_PROMPT.format(section=c.section, text=text))
        return [{"chunk_id": c.id, "query": q["q"], "lang": q.get("lang", "en")} for q in qs if isinstance(q, dict) and q.get("q")]
    n = 3 if c.doc_id == "is456" else 2
    qs = ask(client, EN_PROMPT.format(section=c.section, text=text, n=n))
    return [{"chunk_id": c.id, "query": q, "lang": "en"} for q in qs if isinstance(q, str) and q.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-bsr", type=int, default=150,
                    help="BSR items get LLM queries; the rest get template queries (finetune.build_dataset)")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if OUT.exists():
        done = {json.loads(l)["chunk_id"] for l in OUT.open(encoding="utf-8")}
    todo = [c for c in select_chunks(args.limit_bsr) if c.id not in done]
    print(f"{len(done)} chunks done, {len(todo)} to go")
    with httpx.Client() as client, ThreadPoolExecutor(args.workers) as ex, OUT.open("a", encoding="utf-8") as f:
        futs = {ex.submit(job, client, c): c for c in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                for row in fut.result():
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
            except Exception as e:  # malformed JSON etc. — skip, rerun resumes
                print("skip", futs[fut].id, type(e).__name__, e)
            if i % 50 == 0:
                print(f"{i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
