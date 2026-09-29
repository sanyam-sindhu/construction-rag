import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    id: str
    doc_id: str
    page: int  # 1-based PDF page, used to deep-link the viewer
    page_label: str  # page number as printed on the page ("B - 12", "47", ...)
    ref: str  # human citation anchor: "Clause 26.4.2", "Item 1.5.2", "पैरा 5.1"
    section: str  # breadcrumb, e.g. "Building Work › Earth Work"
    text: str  # what gets embedded, BM25-indexed and shown to the LLM
    lang: str = "en"
    meta: dict = field(default_factory=dict)


def write_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def read_chunks(path: Path) -> list[Chunk]:
    with path.open(encoding="utf-8") as f:
        return [Chunk(**json.loads(line)) for line in f if line.strip()]


def split_words(text: str, max_words: int = 220, overlap: int = 30) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    out, start = [], 0
    while start < len(words):
        out.append(" ".join(words[start : start + max_words]))
        if start + max_words >= len(words):
            break
        start += max_words - overlap
    return out
