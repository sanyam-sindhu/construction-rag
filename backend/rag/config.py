import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
PDF_DIR = Path(os.getenv("CORPUS_DIR", DATA_DIR / "pdfs"))
PROCESSED_DIR = DATA_DIR / "processed"
CHUNKS_PATH = PROCESSED_DIR / "chunks.jsonl"
INDEX_DIR = DATA_DIR / "index"
MODELS_DIR = ROOT / "models"
TESSDATA_DIR = Path(os.getenv("TESSDATA_PREFIX", DATA_DIR / "tessdata"))

DOCS = {
    "is456": {
        "file": "IS456-2000_concrete-code_EN.pdf",
        "title": "IS 456:2000 Plain and Reinforced Concrete – Code of Practice",
        "short": "IS 456:2000",
        "kind": "Engineering standard (scanned → re-OCR with Tesseract)",
        "lang": "en",
    },
    "bsr": {
        "file": "RHB-BSR-2024_schedule-of-rates_EN.pdf",
        "title": "Rajasthan Housing Board – Basic Schedule of Rates 2024",
        "short": "RHB BSR 2024",
        "kind": "Schedule of rates (table-heavy, born-digital)",
        "lang": "en",
    },
    "pmgsy": {
        "file": "PMGSY-III-guidelines_HINDI_image-only-scan.pdf",
        "title": "प्रधानमंत्री ग्राम सड़क योजना – दिशा-निर्देश (PMGSY Guidelines, Hindi)",
        "short": "PMGSY Guidelines (Hindi)",
        "kind": "Government guidelines (Hindi, image-only scan → OCR)",
        "lang": "hi",
    },
}

# Retrieval
BASE_EMBED_MODEL = os.getenv("BASE_EMBED_MODEL", "intfloat/multilingual-e5-small")
FINETUNED_EMBED_DIR = MODELS_DIR / "e5-small-construction"  # served as "finetuned" (after interpolation)
RAW_FINETUNED_DIR = MODELS_DIR / "e5-small-construction-raw"  # straight out of finetune.train
EMBED_MODEL = os.getenv("EMBED_MODEL", "finetuned")  # "finetuned" | "base" | a HF model id
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.25"))  # RRF weight of BM25 relative to dense (tuned on held-out synthetic set)

# Generation: any OpenAI-compatible endpoint (Ollama by default), or Anthropic if a key is set.
LLM_BACKEND = os.getenv("LLM_BACKEND", "auto")  # auto | openai | anthropic | none
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:4b")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
