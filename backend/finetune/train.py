"""Fine-tune intfloat/multilingual-e5-small for this corpus.

    python -m finetune.train [--epochs 1] [--batch-size 32] [--cached]

Contrastive training on (query, positive chunk, hard-negative chunk) triplets with
Multiple-Negatives Ranking loss: besides its mined hard negative, every other passage
in the batch is a negative too. ~3.8k triplets, one epoch: ~25 min on an M-series Mac
(MPS), a couple of minutes on any CUDA GPU.
"""

import argparse
import json
import random

import torch
from datasets import Dataset
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.losses import CachedMultipleNegativesRankingLoss, MultipleNegativesRankingLoss
from sentence_transformers.training_args import BatchSamplers

from rag.chunk import read_chunks
from rag.config import BASE_EMBED_MODEL, CHUNKS_PATH, DATA_DIR, FINETUNED_EMBED_DIR, MODELS_DIR, RAW_FINETUNED_DIR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=float, default=1)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=4e-5)
    ap.add_argument("--max-seq-length", type=int, default=256)
    ap.add_argument("--cached", action="store_true",
                    help="CachedMNRL: larger effective batch at ~2x compute (worth it on a real GPU)")
    args = ap.parse_args()

    random.seed(42)
    texts = {c.id: c.text for c in read_chunks(CHUNKS_PATH)}
    rows = [json.loads(l) for l in (DATA_DIR / "finetune" / "train.jsonl").open(encoding="utf-8")]
    random.shuffle(rows)
    ds = Dataset.from_dict({
        "anchor": [f"query: {r['query']}" for r in rows],
        "positive": [f"passage: {texts[r['pos']]}" for r in rows],
        "negative": [f"passage: {texts[r['neg']]}" for r in rows],
    })
    print(f"{len(ds)} training triplets")

    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    # Attention dropout off: PyTorch's fused SDPA kernel on MPS doesn't support it, and the eager
    # fallback materialises every attention matrix (17 GB on a laptop). Hidden dropout stays on.
    model = SentenceTransformer(BASE_EMBED_MODEL, device=device, config_kwargs={"attention_probs_dropout_prob": 0.0})
    model.max_seq_length = args.max_seq_length
    loss = (CachedMultipleNegativesRankingLoss(model, mini_batch_size=16) if args.cached
            else MultipleNegativesRankingLoss(model))

    targs = SentenceTransformerTrainingArguments(
        output_dir=str(MODELS_DIR / "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        warmup_ratio=0.1,
        weight_decay=0.01,
        batch_sampler=BatchSamplers.NO_DUPLICATES,  # duplicate positives in a batch would be false negatives
        logging_steps=10,
        save_strategy="no",
        report_to=[],
        seed=42,
    )
    trainer = SentenceTransformerTrainer(model=model, args=targs, train_dataset=ds, loss=loss)
    trainer.train()
    model.save(str(RAW_FINETUNED_DIR))
    model.save(str(FINETUNED_EMBED_DIR))  # served until finetune.interpolate replaces it
    print(f"saved → {RAW_FINETUNED_DIR} (+ copy served from {FINETUNED_EMBED_DIR}); next: python -m finetune.interpolate")


if __name__ == "__main__":
    main()
