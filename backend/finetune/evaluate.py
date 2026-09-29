"""Retrieval evaluation: BM25 vs dense (base / fine-tuned) vs hybrid.

    python -m finetune.evaluate            → eval/results.md

Two query sets:
  handwritten  eval/questions.jsonl — 47 questions written by hand against the PDFs, gold
               chunks verified manually; their chunks were excluded from fine-tuning.
  synthetic    data/finetune/test_synth.jsonl — LLM questions for 15% held-out chunks.
Metrics: Recall@1/5/10 (any gold chunk in top-k) and MRR@10.
"""

import json
from collections import defaultdict

from rag.config import DATA_DIR, FINETUNED_EMBED_DIR, RAW_FINETUNED_DIR, ROOT
from rag.retrieval import Retriever

SWEEP = [0.0, 0.25, 0.5, 0.75, 1.0]


def load(path):
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def metrics(ranks: list[int | None]) -> dict:
    n = len(ranks)
    return {"n": n,
            "R@1": sum(1 for r in ranks if r and r <= 1) / n,
            "R@5": sum(1 for r in ranks if r and r <= 5) / n,
            "R@10": sum(1 for r in ranks if r and r <= 10) / n,
            "MRR@10": sum(1 / r for r in ranks if r and r <= 10) / n}


def run(retriever: Retriever, questions: list[dict], mode: str, model: str, w: float = 1.0) -> list[dict]:
    out = []
    for q in questions:
        hits = retriever.search(q["question"] if "question" in q else q["query"], k=10, mode=mode, model=model,
                                bm25_weight=w)
        ids = [h.chunk.id for h in hits]
        rank = next((i + 1 for i, cid in enumerate(ids) if cid in set(q["gold"])), None)
        out.append({**q, "rank": rank, "top": ids[:3]})
    return out


def slice_key(q) -> str:
    if q["doc"] == "pmgsy":
        return "PMGSY (Hindi) · Hindi query" if q.get("lang") == "hi" else "PMGSY (Hindi) · English query"
    return {"is456": "IS 456", "bsr": "BSR"}[q["doc"]]


def main():
    sets = {"handwritten": load(ROOT / "eval" / "questions.jsonl")}
    synth = DATA_DIR / "finetune" / "test_synth.jsonl"
    if synth.exists():
        sets["synthetic held-out"] = load(synth)

    r = Retriever()
    tuned = "finetuned" if FINETUNED_EMBED_DIR.exists() else "base"

    # Pick the BM25 fusion weight on the synthetic held-out set (never on the hand-written set).
    sweep = {}
    if "synthetic held-out" in sets:
        for w in SWEEP:
            ranks = [row["rank"] for row in run(r, sets["synthetic held-out"], "hybrid", tuned, w)]
            sweep[w] = metrics(ranks)
            print(f"sweep w={w}: MRR@10={sweep[w]['MRR@10']:.3f} R@5={sweep[w]['R@5']:.3f}")
    # Tie-break towards keeping BM25: among weights within 0.01 MRR of the best, take the largest —
    # a lexical safety net for exact tokens (new item codes, part numbers) no validation set covers.
    top = max((m["MRR@10"] for m in sweep.values()), default=0)
    best_w = max((w for w, m in sweep.items() if m["MRR@10"] >= top - 0.01), default=0.5)

    configs = [("BM25", "bm25", "base", 1.0), ("Dense · base e5", "dense", "base", 1.0),
               ("Hybrid, plain RRF · base e5", "hybrid", "base", 1.0),
               (f"Hybrid, weighted RRF (w={best_w}) · base e5", "hybrid", "base", best_w)]
    if RAW_FINETUNED_DIR.exists() and (ROOT / "eval" / "interpolation.json").exists():
        configs += [("Dense · fine-tuned e5, raw", "dense", str(RAW_FINETUNED_DIR), 1.0)]
    if FINETUNED_EMBED_DIR.exists():
        configs += [("Dense · fine-tuned e5 (served)", "dense", "finetuned", 1.0),
                    (f"Hybrid, weighted RRF (w={best_w}) · fine-tuned e5 (served)", "hybrid", "finetuned", best_w)]
    results, per_question = {}, {}
    for set_name, qs in sets.items():
        for label, mode, model, w in configs:
            rows = run(r, qs, mode, model, w)
            slices = defaultdict(list)
            for row in rows:
                slices["all"].append(row["rank"])
                slices[slice_key(row)].append(row["rank"])
            results[(set_name, label)] = {k: metrics(v) for k, v in slices.items()}
            if set_name == "handwritten":
                per_question[label] = {row["id"]: row["rank"] for row in rows}
            print(f"{set_name:20s} {label:22s} " + "  ".join(f"{k}={v:.3f}" for k, v in results[(set_name, label)]['all'].items() if k != 'n'))

    lines = ["# Retrieval evaluation", "",
             "Recall@k = share of questions with a gold chunk in the top k. MRR@10 = mean reciprocal rank.", ""]
    for set_name, qs in sets.items():
        lines += [f"## {set_name} ({len(qs)} questions)", "", "| Retriever | R@1 | R@5 | R@10 | MRR@10 |", "|---|---|---|---|---|"]
        for label, *_ in configs:
            m = results[(set_name, label)]["all"]
            lines.append(f"| {label} | {m['R@1']:.2f} | {m['R@5']:.2f} | {m['R@10']:.2f} | {m['MRR@10']:.2f} |")
        slice_names = [k for k in results[(set_name, configs[0][0])] if k != "all"]
        lines += ["", "Recall@5 by slice:", "", "| Retriever | " + " | ".join(f"{s} (n={results[(set_name, configs[0][0])][s]['n']})" for s in slice_names) + " |",
                  "|---|" + "---|" * len(slice_names)]
        for label, *_ in configs:
            lines.append(f"| {label} | " + " | ".join(f"{results[(set_name, label)][s]['R@5']:.2f}" for s in slice_names) + " |")
        lines.append("")
    if sweep:
        lines += [f"## BM25 fusion weight sweep (synthetic held-out, {tuned} e5) → chose w={best_w}", "",
                  "| BM25 weight | R@1 | R@5 | MRR@10 |", "|---|---|---|---|"]
        lines += [f"| {w} | {m['R@1']:.2f} | {m['R@5']:.2f} | {m['MRR@10']:.2f} |" for w, m in sweep.items()]
        lines.append("")
    if per_question:
        labels = list(per_question)
        lines += ["## Handwritten: rank of first gold chunk per question (– = not in top 10)", "",
                  "| id | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
        for qid in per_question[labels[0]]:
            lines.append(f"| {qid} | " + " | ".join(str(per_question[l][qid] or "–") for l in labels) + " |")
    (ROOT / "eval" / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote eval/results.md")


if __name__ == "__main__":
    main()
