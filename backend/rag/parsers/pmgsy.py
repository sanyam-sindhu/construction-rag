"""Parser for the PMGSY guidelines (Hindi, image-only scan, 46 pages).

No text layer at all, so everything comes from Tesseract `hin+eng` (tessdata_best).
Body text OCRs cleanly; the weak spot is the paragraph numbers in the left margin
("5.1" → "54", "5.2..." with leader dots). We repair them from document structure:
under heading 5, a mangled sub-number whose digits start with 5 becomes 5.(prev+1).
Correct numbers matter because they are the citation anchor ("पैरा 5.1").
"""

import re

from ..chunk import Chunk
from ..config import PROCESSED_DIR
from ..ocr import ocr_pdf, page_line_boxes, window_boxes

DOC_ID = "pmgsy"
PAGES = list(range(1, 47))
FRONT_MATTER = {1, 2, 3, 4}  # cover, index, contents

DOTTED_RE = re.compile(r"^(\d{1,2})[.,](\d{1,2})(?:[.,](\d{1,2}))?\.*$")
INT_RE = re.compile(r"^(\d{1,2})\.*$")
FOOTER_RE = re.compile(r"^(प्रधान\s*मंत्री ग्राम सड़क योजना|\d{1,3})$")


def _para_number(cand: str, alt: str, heading: bool, major: int | None, minor: int):
    """Decide the paragraph number for a margin token. Returns (para, major, minor) or None.

    `alt` is the English/digits-only re-read, which gets digits right far more often than
    the Hindi model (which reads "1" as "4": 10 → 40, 11 → 44) but tends to drop dots.
    """
    if "(" in cand or "(" in alt or ")" in alt:
        return None  # list markers (i), (ii), (क) …
    if re.search(r"[ऀ-ॿ]", cand) and not DOTTED_RE.match(alt):
        return None  # a Hindi word, not a number
    if major is not None:
        for c in (alt, cand):
            if (m := DOTTED_RE.match(c)) and int(m.group(1)) == major and 0 <= int(m.group(2)) - minor <= 3:
                sub = int(m.group(2))
                return f"{major}.{sub}" + (f".{m.group(3)}" if m.group(3) else ""), major, sub
    if heading:
        for c in (alt, cand):
            if m := INT_RE.match(c.rstrip(".")):
                n = int(m.group(1))
                if major is None or 0 < n - major <= 2:
                    return str(n), n, 0
        if major is not None and re.search(r"\d", cand + alt):
            return str(major + 1), major + 1, 0
        return None
    if major is None:
        return None
    digits = [re.sub(r"\D", "", c) for c in (alt, cand)]
    if any(len(d) >= 2 and d.startswith(str(major)) for d in digits):
        return f"{major}.{minor + 1}", major, minor + 1  # dot lost ("51" for 5.1): trust the sequence
    return None


def _norm(t: str) -> str:
    t = t.replace("|", "।").replace("…", " ")
    t = re.sub(r"\.{2,}", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def parse(pdf_path) -> list[Chunk]:
    pages = ocr_pdf(pdf_path, PAGES, PROCESSED_DIR / "ocr" / "pmgsy.json",
                    lang="hin+eng", psm=4, two_column=False, margin_alt=True)

    major, minor = None, 0
    segments = []
    cur = {"para": None, "title": "", "page": 1, "lines": []}
    for pno in PAGES:
        info = pages[pno]
        width = info["width"]
        for li, ln in enumerate(info["lines"]):
            text = ln["text"].strip()
            if not text or ln["x0"] < 0.05 * width:  # coloured page-number tab at the edge
                continue
            first, _, rest = text.partition(" ")
            para = None
            if pno not in FRONT_MATTER and "alt" in ln and 0.10 * width < ln["x0"] < 0.20 * width:
                heading = ln["x0"] < 0.15 * width  # major headings sit further left
                res = _para_number(first, ln.get("alt", ""), heading, major, minor)
                if res:
                    para, major, minor = res
            if para:
                segments.append(cur)
                cur = {"para": para, "title": "", "page": pno, "lines": []}
                text = rest
                if "." not in para:
                    cur["title"] = _norm(rest)
            if FOOTER_RE.match(_norm(text)):
                continue
            cur["lines"].append((pno, _norm(text), li))
    segments.append(cur)

    # Attach headings' titles to their sub-paragraphs, then pack into ~180-word chunks.
    line_boxes = {p: page_line_boxes(pages[p]) for p in pages}
    titles = {s["para"]: s["title"] for s in segments if s["para"] and "." not in s["para"]}
    chunks, buf = [], []

    def emit(buf):
        paras = [s["para"] for s in buf if s["para"]]
        words = [(w, p, li) for s in buf for p, t, li in s["lines"] for w in t.split()]
        if not words:
            return
        top = (paras[0] or "").split(".")[0] if paras else ""
        crumbs = " › ".join(filter(None, ["PMGSY दिशा-निर्देश", f"{top} {titles.get(top, '')}".strip() if top else "प्रस्तावना"]))
        ref = (f"पैरा {paras[0]}" if len(paras) <= 1 else f"पैरा {paras[0]}–{paras[-1]}") if paras else f"पृष्ठ {words[0][1]}"
        for i in range(0, max(len(words) - 30, 1), 200):
            win = words[i:i + 230]
            chunks.append(Chunk(
                id=f"pmgsy-{len(chunks)}", doc_id=DOC_ID, page=win[0][1], page_label=str(win[0][1]),
                ref=ref, section=crumbs, text=f"[{crumbs}]\n" + " ".join(w for w, _, _ in win), lang="hi",
                meta={"type": "para", "paras": paras, "boxes": window_boxes(win, line_boxes)}))

    for seg in segments:
        n = sum(len(t.split()) for _, t, _ in seg["lines"])
        size = sum(len(t.split()) for s in buf for _, t, _ in s["lines"])
        same_top = buf and (seg["para"] or "").split(".")[0] == (buf[0]["para"] or "").split(".")[0]
        if buf and (not same_top or size + n > 180):
            emit(buf)
            buf = []
        buf.append(seg)
    if buf:
        emit(buf)
    return chunks
