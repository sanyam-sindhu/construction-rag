"""End-to-end check of generated answers on the hand-written questions.

    python -m finetune.eval_answers [--model finetuned|base] [--limit N]

For each question: retrieve (hybrid), generate with the configured LLM, then check
  facts  – every key-fact regex from eval/questions.jsonl (the expected rate / value / term)
           appears in the answer
  cites  – the answer cites at least one gold source
Writes eval/answers.md with every answer, so failures can be read, not just counted.
"""

import argparse
import json
import re
import time

from rag.config import DOCS, ROOT
from rag.generate import backend_info, cited_numbers, stream_answer
from rag.retrieval import Retriever


def normalise(text: str) -> str:
    # "1,56,300" / "5,260.00" → "156300" / "5260.00" so numeric keys match Indian digit grouping
    return re.sub(r"(?<=\d),(?=\d)", "", text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="finetuned")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    qs = [json.loads(l) for l in (ROOT / "eval" / "questions.jsonl").open(encoding="utf-8")]
    if args.limit:
        qs = qs[: args.limit]
    r = Retriever()
    info = backend_info()
    rows = []
    for q in qs:
        t = time.time()
        hits = r.search(q["question"], k=args.k, model=args.model)
        answer = "".join(stream_answer(q["question"], hits))
        cited = cited_numbers(answer, len(hits))
        facts = all(re.search(k, normalise(answer), re.I) for k in q["keys"])
        cites_gold = any(hits[n - 1].chunk.id in q["gold"] for n in cited)
        retrieved_gold = any(h.chunk.id in q["gold"] for h in hits)
        rows.append({**q, "expected": q["answer"], "answer": answer, "facts": facts, "cites_gold": cites_gold,
                     "retrieved_gold": retrieved_gold, "secs": time.time() - t,
                     "sources": [f"[{i}] {DOCS[h.chunk.doc_id]['short']} {h.chunk.ref}" for i, h in enumerate(hits, 1)]})
        print(f"{q['id']:7s} facts={'✓' if facts else '✗'} cites_gold={'✓' if cites_gold else '✗'} "
              f"retrieved={'✓' if retrieved_gold else '✗'} {rows[-1]['secs']:.1f}s")

    n = len(rows)
    by_doc = {}
    for row in rows:
        by_doc.setdefault(row["doc"], []).append(row)
    lines = [f"# End-to-end answer check ({info['model']}, {args.model} retriever, k={args.k})", "",
             "`facts` = every expected key fact (rate, value, term) appears in the answer; "
             "`cites gold` = the answer cites a source that is a gold chunk.", "",
             "| Slice | n | gold retrieved | key facts in answer | cites a gold source |", "|---|---|---|---|---|"]
    for name, rs in [("all", rows)] + sorted(by_doc.items()):
        lines.append(f"| {name} | {len(rs)} | {sum(x['retrieved_gold'] for x in rs) / len(rs):.0%} | "
                     f"{sum(x['facts'] for x in rs) / len(rs):.0%} | {sum(x['cites_gold'] for x in rs) / len(rs):.0%} |")
    lines += ["", f"Mean latency {sum(x['secs'] for x in rows) / n:.1f}s per question (retrieval + generation).", ""]
    for row in rows:
        lines += [f"### {row['id']} — {'✓' if row['facts'] else '✗'} facts · {'✓' if row['cites_gold'] else '✗'} cites gold",
                  f"**Q:** {row['question']}  ", f"**Expected:** {row['expected']}  ",
                  f"**Sources:** {'; '.join(row['sources'])}", "", row["answer"].strip(), ""]
    (ROOT / "eval" / "answers.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"facts {sum(x['facts'] for x in rows)}/{n}  cites_gold {sum(x['cites_gold'] for x in rows)}/{n}  → eval/answers.md")


if __name__ == "__main__":
    main()
