"""Weight-space interpolation between the base and fine-tuned retriever (WiSE-FT).

    python -m finetune.interpolate [--alphas 0.3 0.5 0.7]

θ(α) = (1-α)·θ_base + α·θ_finetuned. Fine-tuning on 3.8k synthetic triplets fixed the
cross-lingual and near-duplicate failures but also taught the model to over-weight bare
numbers ("40 m3" → "40 mm thick"), costing top-1 precision on general questions.
Interpolating recovers the base model's robustness while keeping most of the gain
(Wortsman et al., 2022). α is chosen on the synthetic held-out set only; the chosen
model is written to models/e5-small-construction (what the app serves as "fine-tuned").
"""

import argparse
import json
import shutil

import numpy as np
import torch

from rag.config import BASE_EMBED_MODEL, DATA_DIR, FINETUNED_EMBED_DIR, RAW_FINETUNED_DIR, ROOT
from rag.retrieval import Retriever, encode_passages, encode_queries

RAW_DIR = RAW_FINETUNED_DIR


def dense_metrics(r: Retriever, emb: np.ndarray, model, qs: list[dict]) -> dict:
    qemb = encode_queries(model, [q.get("question") or q["query"] for q in qs])
    order = np.argsort(-(qemb @ emb.T), axis=1)[:, :10]
    ranks = []
    for q, idx in zip(qs, order):
        ids = [r.chunks[i].id for i in idx]
        ranks.append(next((i + 1 for i, cid in enumerate(ids) if cid in q["gold"]), None))
    n = len(ranks)
    return {"R@1": round(sum(1 for x in ranks if x == 1) / n, 3), "R@5": round(sum(1 for x in ranks if x and x <= 5) / n, 3),
            "MRR@10": round(sum(1 / x for x in ranks if x) / n, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.3, 0.5, 0.7])
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer

    if not RAW_DIR.exists():
        raise SystemExit(f"{RAW_DIR} not found: run `python -m finetune.train` first")
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    sd_base = {k: v.clone() for k, v in SentenceTransformer(BASE_EMBED_MODEL, device="cpu").state_dict().items()}
    model = SentenceTransformer(str(RAW_DIR), device="cpu")
    sd_raw = {k: v.clone() for k, v in model.state_dict().items()}
    model.to(device)
    model.max_seq_length = 512  # same as serving (training used 256)

    def set_alpha(a: float):
        model.load_state_dict({k: (1 - a) * sd_base[k] + a * sd_raw[k] if sd_raw[k].is_floating_point() else sd_raw[k]
                               for k in sd_raw})

    synth = [json.loads(l) for l in (DATA_DIR / "finetune" / "test_synth.jsonl").open(encoding="utf-8")]
    hand = [json.loads(l) for l in (ROOT / "eval" / "questions.jsonl").open(encoding="utf-8")]
    r = Retriever()
    results = {}
    for a in args.alphas:
        set_alpha(a)
        emb = encode_passages(model, [c.text for c in r.chunks])
        results[a] = {"synthetic": dense_metrics(r, emb, model, synth), "handwritten": dense_metrics(r, emb, model, hand)}
        print(f"α={a:.2f}  synthetic {results[a]['synthetic']}  handwritten {results[a]['handwritten']}", flush=True)

    best = max(results, key=lambda a: results[a]["synthetic"]["MRR@10"])
    set_alpha(best)
    shutil.rmtree(FINETUNED_EMBED_DIR, ignore_errors=True)
    model.save(str(FINETUNED_EMBED_DIR))
    (ROOT / "eval" / "interpolation.json").write_text(json.dumps({"chosen_alpha": best, "results": results}, indent=1))
    print(f"chose α={best} (best synthetic MRR@10) → {FINETUNED_EMBED_DIR}")


if __name__ == "__main__":
    main()
