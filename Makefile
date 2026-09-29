PY := $(CURDIR)/.venv/bin/python
PORT ?= 8765

.PHONY: setup ingest dataset train interpolate eval eval-answers api ui ask

setup:            ## create venv, install backend + frontend deps
	python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

ingest:           ## parse PDFs in data/pdfs → data/processed/chunks.jsonl
	cd backend && $(PY) -m rag.ingest

dataset:          ## rebuild fine-tuning triplets (needs data/finetune/queries.jsonl)
	cd backend && $(PY) -m finetune.build_dataset

train:            ## fine-tune the retriever → models/e5-small-construction
	cd backend && PYTORCH_ENABLE_MPS_FALLBACK=1 $(PY) -m finetune.train

interpolate:      ## WiSE-FT: blend base + fine-tuned weights, α picked on held-out data
	cd backend && $(PY) -m finetune.interpolate

eval:             ## retrieval metrics → eval/results.md
	cd backend && $(PY) -m finetune.evaluate

eval-answers:     ## end-to-end answer check (needs the LLM) → eval/answers.md
	cd backend && $(PY) -m finetune.eval_answers

api:              ## FastAPI on :8765
	cd backend && $(PY) -m uvicorn rag.api:app --port $(PORT)

ui:               ## React dev server on :5173 (proxies /api to :8765)
	cd frontend && npm run dev

ask:              ## make ask Q="your question"
	cd backend && $(PY) -m rag.cli "$(Q)"
