"""Ask a question from the terminal.

    python -m rag.cli "What is the minimum nominal cover for severe exposure?"
    python -m rag.cli --docs bsr --k 8 "rate of 400 mm DI K-9 pipe"
    python -m rag.cli --search-only "PMGSY maintenance contract"
"""

import argparse
import sys

from .config import DOCS
from .generate import backend_info, cited_numbers, stream_answer
from .retrieval import Retriever


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--docs", nargs="*", choices=list(DOCS), help="restrict to these documents")
    ap.add_argument("--mode", default="hybrid", choices=["hybrid", "dense", "bm25"])
    ap.add_argument("--model", default="finetuned", choices=["finetuned", "base"])
    ap.add_argument("--search-only", action="store_true", help="skip the LLM, just show retrieved sources")
    args = ap.parse_args()

    hits = Retriever().search(args.question, k=args.k, docs=args.docs, mode=args.mode, model=args.model)
    answer = ""
    if not args.search_only:
        print(f"\n[{backend_info()['model']}]\n")
        for tok in stream_answer(args.question, hits):
            answer += tok
            sys.stdout.write(tok)
            sys.stdout.flush()
        print("\n")
    cited = set(cited_numbers(answer, len(hits)))
    print("Sources:")
    for n, h in enumerate(hits, 1):
        c = h.chunk
        mark = "*" if n in cited else " "
        print(f" {mark}[{n}] {DOCS[c.doc_id]['short']} — {c.ref} — printed p. {c.page_label} (PDF p. {c.page})")


if __name__ == "__main__":
    main()
