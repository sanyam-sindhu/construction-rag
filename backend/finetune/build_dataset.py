"""Assemble the embedding fine-tuning dataset.

    python -m finetune.build_dataset

Inputs
  data/finetune/queries.jsonl   LLM-written queries (finetune.gen_queries): IS 456, PMGSY
                                (English + Hindi), a sample of BSR items
  data/processed/chunks.jsonl   parsed corpus; BSR rows also get cheap template queries
  eval/questions.jsonl          hand-written evaluation set → its gold chunks are EXCLUDED

Outputs (data/finetune/)
  train.jsonl       {"query", "pos", "neg"} triplets (chunk ids), hard negatives mined with the base model
  test_synth.jsonl  LLM queries for a 15% held-out set of chunks, never trained on

Why templates for BSR: the LLM runs at ~20 tok/s on a laptop, too slow for 8k rows, and
the skill BSR needs is discrimination between sibling rows (250 vs 300 mm dia), which
hard-negative training on templated queries teaches directly.
"""

import json
import random
import re
from collections import defaultdict

import numpy as np

from rag.chunk import read_chunks
from rag.config import CHUNKS_PATH, DATA_DIR, ROOT
from rag.retrieval import Retriever, encode_queries, load_encoder, resolve_model

OUT_DIR = DATA_DIR / "finetune"
HELDOUT_FRAC = 0.15
N_TEMPLATE_ITEMS = 1200  # kept small so templated BSR pairs don't drown the LLM-written ones
UPSAMPLE_NATURAL = 2  # LLM-written and heading queries are seen twice per epoch
N_BSR_HELDOUT = 60
SEED = 7

BOILER = re.compile(
    r"^(providing|supplying|supply|manufacturing|lowering|laying|jointing|fixing|fitting|installation|installing|"
    r"testing|commissioning|and|&|,|p\s*&\s*f|s\s*&\s*f|sitc|of|the|in|position|making|construction|providing,)\b[\s,&]*",
    re.I)
TEMPLATES = [
    "{leaf} {kp} rate",
    "rate for {kp} {leaf}",
    "what is the rate of {kp} {leaf}?",
    "{kp} {leaf} cost per {unit}",
    "how much does {leaf} {kp} cost",
    "BSR rate {kp} {leaf}",
    "{leaf} {kp}",
]


def keyphrase(text: str, n: int) -> str:
    t = re.sub(r"\([^)]*\)", " ", text)
    t = re.sub(r"\s+", " ", t).strip()
    for _ in range(6):
        t = BOILER.sub("", t)
    words = t.split()
    return " ".join(words[:n]).rstrip(",.;:-")


def template_queries(c, rng: random.Random) -> list[str]:
    m = c.meta
    parents = m.get("parents", [])
    leaf = keyphrase(m.get("desc", ""), 14)
    kp = " ".join(filter(None, [keyphrase(parents[0], 7) if parents else "", *[keyphrase(p, 6) for p in parents[1:]]]))
    unit = (m.get("unit") or "unit").strip(".").lower()
    out = []
    for tpl in rng.sample(TEMPLATES, 2):
        q = tpl.format(leaf=leaf, kp=kp, unit=unit)
        words = q.split()
        # light word dropout so the model can't rely on exact phrasing
        words = [w for w in words if rng.random() > 0.12 or re.search(r"\d", w)]
        out.append(re.sub(r"\s+", " ", " ".join(words)).strip().lower())
    return out


def group_key(chunk_id: str) -> str:
    # windows of the same clause/paragraph group overlap, so they are not valid negatives of each other
    return re.sub(r"-\d+$", "", chunk_id) if chunk_id.startswith("is456") else chunk_id


def main():
    rng = random.Random(SEED)
    chunks = read_chunks(CHUNKS_PATH)
    by_id = {c.id: c for c in chunks}

    eval_gold = {g for line in (ROOT / "eval" / "questions.jsonl").open(encoding="utf-8")
                 for g in json.loads(line)["gold"]}
    llm = [json.loads(l) for l in (OUT_DIR / "queries.jsonl").open(encoding="utf-8")]
    llm = [q for q in llm if q["chunk_id"] in by_id]

    llm_chunks = sorted({q["chunk_id"] for q in llm} - eval_gold)
    rng.shuffle(llm_chunks)
    heldout = set(llm_chunks[: int(len(llm_chunks) * HELDOUT_FRAC)])
    excluded = eval_gold | heldout

    pairs = [(q["query"], q["chunk_id"], "llm-" + q.get("lang", "en")) for q in llm if q["chunk_id"] not in excluded]
    # IS 456 chunks the LLM didn't reach: their clause/table headings are natural queries.
    has_llm = {q["chunk_id"] for q in llm}
    for c in chunks:
        if c.doc_id == "is456" and c.id not in has_llm and c.id not in excluded:
            pairs += [(t.lower(), c.id, "title") for t in c.meta.get("titles", [])]
    items = [c for c in chunks if c.doc_id == "bsr" and c.meta.get("type") == "item" and c.meta.get("rate")
             and c.id not in excluded]
    pairs = pairs * UPSAMPLE_NATURAL
    sampled = rng.sample(items, min(N_TEMPLATE_ITEMS + N_BSR_HELDOUT, len(items)))
    bsr_heldout, sampled = sampled[:N_BSR_HELDOUT], sampled[N_BSR_HELDOUT:]
    for c in sampled:
        pairs += [(q, c.id, "template") for q in template_queries(c, rng)]
    test = [{"query": q["query"], "gold": [q["chunk_id"]], "doc": by_id[q["chunk_id"]].doc_id, "lang": q.get("lang", "en")}
            for q in llm if q["chunk_id"] in heldout]
    # BSR had no LLM budget, so its held-out queries are templated (from items never trained on).
    test += [{"query": template_queries(c, rng)[0], "gold": [c.id], "doc": "bsr", "lang": "en"} for c in bsr_heldout]

    # Hard negatives: rank 3-30 under the *base* model, excluding the positive's own group.
    r = Retriever(chunks)
    emb = r.embeddings("base")
    qemb = encode_queries(load_encoder(resolve_model("base")), [p[0] for p in pairs])
    top = np.argsort(-(qemb @ emb.T), axis=1)[:, :30]
    rows = []
    for (q, pos, src), cand in zip(pairs, top):
        negs = [chunks[i].id for i in cand[2:] if group_key(chunks[i].id) != group_key(pos) and chunks[i].id not in eval_gold]
        rows.append({"query": q, "pos": pos, "neg": rng.choice(negs[:10]) if negs else rng.choice(chunks).id, "src": src})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "train.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (OUT_DIR / "test_synth.jsonl").open("w", encoding="utf-8") as f:
        for row in test:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    stats = defaultdict(int)
    for row in rows:
        stats[f"{row['src']}:{row['pos'].split('-')[0]}"] += 1
    print(f"train triplets: {len(rows)}  {dict(sorted(stats.items()))}")
    print(f"held-out chunks: {len(heldout)}  synthetic test queries: {len(test)}  eval-gold chunks excluded: {len(eval_gold)}")


if __name__ == "__main__":
    main()
