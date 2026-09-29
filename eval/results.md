# Retrieval evaluation

Recall@k = share of questions with a gold chunk in the top k. MRR@10 = mean reciprocal rank.

## handwritten (47 questions)

| Retriever | R@1 | R@5 | R@10 | MRR@10 |
|---|---|---|---|---|
| BM25 | 0.62 | 0.70 | 0.77 | 0.66 |
| Dense · base e5 | 0.72 | 0.91 | 0.96 | 0.80 |
| Hybrid, plain RRF · base e5 | 0.66 | 0.87 | 0.94 | 0.75 |
| Hybrid, weighted RRF (w=0.25) · base e5 | 0.70 | 0.89 | 0.96 | 0.78 |
| Dense · fine-tuned e5, raw | 0.57 | 0.94 | 0.96 | 0.74 |
| Dense · fine-tuned e5 (served) | 0.72 | 0.94 | 0.98 | 0.82 |
| Hybrid, weighted RRF (w=0.25) · fine-tuned e5 (served) | 0.68 | 0.96 | 0.98 | 0.79 |

Recall@5 by slice:

| Retriever | IS 456 (n=16) | BSR (n=16) | PMGSY (Hindi) · English query (n=10) | PMGSY (Hindi) · Hindi query (n=5) |
|---|---|---|---|---|
| BM25 | 0.81 | 1.00 | 0.00 | 0.80 |
| Dense · base e5 | 0.94 | 0.94 | 0.80 | 1.00 |
| Hybrid, plain RRF · base e5 | 0.88 | 1.00 | 0.60 | 1.00 |
| Hybrid, weighted RRF (w=0.25) · base e5 | 0.94 | 0.94 | 0.70 | 1.00 |
| Dense · fine-tuned e5, raw | 0.88 | 1.00 | 0.90 | 1.00 |
| Dense · fine-tuned e5 (served) | 0.94 | 1.00 | 0.80 | 1.00 |
| Hybrid, weighted RRF (w=0.25) · fine-tuned e5 (served) | 1.00 | 1.00 | 0.80 | 1.00 |

## synthetic held-out (150 questions)

| Retriever | R@1 | R@5 | R@10 | MRR@10 |
|---|---|---|---|---|
| BM25 | 0.59 | 0.81 | 0.84 | 0.68 |
| Dense · base e5 | 0.56 | 0.84 | 0.91 | 0.68 |
| Hybrid, plain RRF · base e5 | 0.62 | 0.85 | 0.91 | 0.72 |
| Hybrid, weighted RRF (w=0.25) · base e5 | 0.59 | 0.86 | 0.91 | 0.70 |
| Dense · fine-tuned e5, raw | 0.64 | 0.92 | 0.97 | 0.76 |
| Dense · fine-tuned e5 (served) | 0.67 | 0.90 | 0.97 | 0.77 |
| Hybrid, weighted RRF (w=0.25) · fine-tuned e5 (served) | 0.67 | 0.91 | 0.97 | 0.77 |

Recall@5 by slice:

| Retriever | IS 456 (n=69) | PMGSY (Hindi) · English query (n=14) | PMGSY (Hindi) · Hindi query (n=7) | BSR (n=60) |
|---|---|---|---|---|
| BM25 | 0.83 | 0.00 | 1.00 | 0.95 |
| Dense · base e5 | 0.84 | 0.71 | 1.00 | 0.85 |
| Hybrid, plain RRF · base e5 | 0.87 | 0.29 | 1.00 | 0.93 |
| Hybrid, weighted RRF (w=0.25) · base e5 | 0.87 | 0.64 | 1.00 | 0.88 |
| Dense · fine-tuned e5, raw | 0.91 | 0.79 | 1.00 | 0.95 |
| Dense · fine-tuned e5 (served) | 0.87 | 0.71 | 1.00 | 0.97 |
| Hybrid, weighted RRF (w=0.25) · fine-tuned e5 (served) | 0.90 | 0.64 | 1.00 | 0.98 |

## BM25 fusion weight sweep (synthetic held-out, finetuned e5) → chose w=0.25

| BM25 weight | R@1 | R@5 | MRR@10 |
|---|---|---|---|
| 0.0 | 0.67 | 0.90 | 0.77 |
| 0.25 | 0.67 | 0.91 | 0.77 |
| 0.5 | 0.67 | 0.90 | 0.76 |
| 0.75 | 0.65 | 0.89 | 0.75 |
| 1.0 | 0.63 | 0.89 | 0.74 |

## Handwritten: rank of first gold chunk per question (– = not in top 10)

| id | BM25 | Dense · base e5 | Hybrid, plain RRF · base e5 | Hybrid, weighted RRF (w=0.25) · base e5 | Dense · fine-tuned e5, raw | Dense · fine-tuned e5 (served) | Hybrid, weighted RRF (w=0.25) · fine-tuned e5 (served) |
|---|---|---|---|---|---|---|---|
| is-01 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-02 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-03 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-04 | 3 | 1 | 2 | 1 | 2 | 2 | 2 |
| is-05 | 1 | 4 | 1 | 1 | – | 8 | 2 |
| is-06 | 1 | 1 | 1 | 1 | 4 | 2 | 2 |
| is-07 | 1 | 1 | 1 | 1 | 2 | 1 | 1 |
| is-08 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-09 | 6 | 2 | 3 | 3 | 2 | 2 | 2 |
| is-10 | 1 | 1 | 1 | 1 | 2 | 1 | 1 |
| is-11 | 1 | 1 | 1 | 1 | 2 | 1 | 1 |
| is-12 | – | 5 | 6 | 5 | – | 5 | 5 |
| is-13 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-14 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| is-15 | 8 | 9 | 6 | 8 | 3 | 3 | 3 |
| is-16 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-01 | 1 | 1 | 1 | 1 | 2 | 1 | 1 |
| bsr-02 | 1 | 7 | 1 | 6 | 1 | 1 | 1 |
| bsr-03 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-04 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-05 | 3 | 1 | 2 | 1 | 1 | 1 | 1 |
| bsr-06 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-07 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-08 | 1 | 1 | 1 | 1 | 2 | 1 | 1 |
| bsr-09 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-10 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-11 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-12 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| bsr-13 | 1 | 3 | 1 | 3 | 2 | 3 | 3 |
| bsr-14 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| bsr-15 | 2 | 1 | 1 | 1 | 2 | 1 | 1 |
| bsr-16 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| pm-01 | – | 1 | 1 | 1 | 3 | 2 | 1 |
| pm-02 | – | – | – | – | 10 | – | – |
| pm-03 | – | 1 | 2 | 1 | 1 | 1 | 1 |
| pm-04 | – | – | – | – | 5 | 10 | 10 |
| pm-05 | – | 4 | – | 9 | 1 | 1 | 5 |
| pm-06 | – | 2 | 5 | 2 | 1 | 1 | 3 |
| pm-07 | – | 1 | 5 | 2 | 2 | 2 | 3 |
| pm-08 | – | 1 | 4 | 2 | 1 | 1 | 1 |
| pm-09 | – | 1 | 2 | 1 | 1 | 1 | 1 |
| pm-10 | – | 1 | 8 | 5 | 1 | 1 | 4 |
| pm-11 | 7 | 2 | 3 | 3 | 2 | 3 | 3 |
| pm-12 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| pm-13 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| pm-14 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| pm-15 | 1 | 2 | 1 | 1 | 2 | 1 | 1 |
