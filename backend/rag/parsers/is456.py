"""Parser for IS 456:2000 (Plain and Reinforced Concrete – Code of Practice).

The PDF is a scan whose embedded OCR layer is poor ("ThisIndianStandard",
"Nominal Cencrete Cover", tables flattened to one value per line). We re-OCR the
pages with Tesseract (tessdata_best) plus a gutter-aware reading-order pass, then
chunk along the clause structure so every chunk can be cited as "Clause 26.4.2" or
"Table 16" with the page it starts on.
"""

import re

from ..chunk import Chunk, split_words
from ..config import PROCESSED_DIR
from ..ocr import ocr_pdf, page_line_boxes, window_boxes

DOC_ID = "is456"
AMENDMENT_PAGES = list(range(11, 18))
BODY_PAGES = list(range(21, 112))
PRINTED_OFFSET = 13  # PDF page 24 is printed page 11

SECTION_RE = re.compile(r"^SECTION\s+(\d)\s+(.+)$")
TOP_RE = re.compile(r"^(\d{1,2})\s+([A-Z][A-Z ,:;&'()/\-]{3,})$")
SUB_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){1,4})\s+([A-Za-z(].*)$")
TABLE_RE = re.compile(r"^Table\s+(\d{1,2}[A-Z]?)\s+(.+)$")
ANNEX_RE = re.compile(r"^ANNEX\s+([A-H])\b")
ANNEX_SUB_RE = re.compile(r"^([A-H]-\d{1,2}(?:\.\d{1,2}){0,3})\s+([A-Za-z(].*)$")
NOISE_RE = re.compile(r"^(IS\s*[:.]?\s*4\S*\s*[:.]?\s*\S*|\d{1,3}|[\W_]{1,4})$")


def _is_title(t: str) -> bool:
    """Short, mostly Title-Case line → a heading ("Nominal Cover to Meet Durability Requirement")."""
    words = t.split()
    return 2 <= len(words) <= 12 and sum(w[:1].isupper() for w in words) >= 0.5 * len(words)


def _label(pno):
    if pno in AMENDMENT_PAGES:
        return f"Amendment slip (PDF p.{pno})"
    return str(pno - PRINTED_OFFSET)


def _clean(s):
    s = s.replace("—", "-").replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip()


def parse(pdf_path) -> list[Chunk]:
    pages = ocr_pdf(pdf_path, AMENDMENT_PAGES + BODY_PAGES, PROCESSED_DIR / "ocr" / "is456.json",
                    lang="eng", psm=3, two_column=True)
    chunks: list[Chunk] = []

    # Amendments: short slips, keep one chunk group per page.
    for pno in AMENDMENT_PAGES:
        text = _clean(" ".join(l["text"] for l in pages[pno]["lines"]))
        for i, part in enumerate(split_words(text, 200, 30)):
            chunks.append(Chunk(id=f"is456-amd-p{pno}-{i}", doc_id=DOC_ID, page=pno, page_label=_label(pno),
                                ref="Amendment", section="IS 456:2000 › Amendments", text=part,
                                meta={"type": "amendment"}))

    # Body: split the text stream into clause segments.
    segments = []  # dict(ref, key, title, page, lines)
    section, top_title = "Foreword", ""
    cur = {"ref": "Foreword", "key": "foreword", "title": "", "page": BODY_PAGES[0], "lines": [],
           "section": section, "top": ""}
    last_top = 0
    line_boxes = {p: page_line_boxes(pages[p]) for p in pages}
    for pno in BODY_PAGES:
        for li, ln in enumerate(pages[pno]["lines"]):
            t = _clean(ln["text"])
            if not t or NOISE_RE.match(t):
                continue
            new = None
            if m := SECTION_RE.match(t):
                section = f"Section {m.group(1)} {m.group(2).title()}"
                continue
            if m := TOP_RE.match(t):
                n = int(m.group(1))
                if last_top <= n <= last_top + 3:  # clause numbers only go forward
                    last_top, top_title = n, f"{n} {m.group(2).title()}"
                    new = (f"Clause {n}", str(n), m.group(2).title())
            elif m := SUB_RE.match(t):
                num = m.group(1)
                if abs(int(num.split(".")[0]) - last_top) <= 1:
                    new = (f"Clause {num}", num.split(".")[0], m.group(2))
            elif m := TABLE_RE.match(t):
                new = (f"Table {m.group(1)}", cur["key"], m.group(2))
            elif m := ANNEX_RE.match(t):
                section = f"Annex {m.group(1)}"
                top_title = section
                new = (f"Annex {m.group(1)}", f"annex-{m.group(1)}", "")
            elif m := ANNEX_SUB_RE.match(t):
                new = (f"Clause {m.group(1)}", cur["key"], m.group(2))
            if new:
                segments.append(cur)
                cur = {"ref": new[0], "key": new[1], "title": new[2], "page": pno, "lines": [],
                       "section": section, "top": top_title}
            cur["lines"].append((pno, t, li))
    segments.append(cur)

    # Merge consecutive small segments of the same top-level clause into ~220-word chunks.
    groups, buf = [], []
    for seg in segments:
        if not seg["lines"]:
            continue
        words = sum(len(t.split()) for s in buf for _, t, _ in s["lines"])
        if buf and (seg["key"] != buf[0]["key"] or words + sum(len(t.split()) for _, t, _ in seg["lines"]) > 220):
            groups.append(buf)
            buf = []
        buf.append(seg)
    if buf:
        groups.append(buf)

    for gi, g in enumerate(groups):
        first = g[0]
        refs = [s["ref"] for s in g]
        ref = refs[0] if len(refs) == 1 else f"{refs[0]} – {refs[-1].removeprefix('Clause ')}"
        crumbs = " › ".join(filter(None, ["IS 456:2000", first["section"], first["top"]]))
        words = [(w, pno, li) for s in g for pno, t, li in s["lines"] for w in t.split()]
        step, size = 260, 300
        for pi, start in enumerate(range(0, max(len(words) - 40, 1), step)):
            win = words[start:start + size]
            part, page = " ".join(w for w, _, _ in win), win[0][1]
            chunks.append(Chunk(
                id=f"is456-{gi}-{pi}", doc_id=DOC_ID, page=page, page_label=_label(page),
                ref=ref, section=crumbs, text=f"[{crumbs}]\n{part}",
                meta={"type": "clause", "refs": refs, "titles": [t for t in (s["title"] for s in g) if _is_title(t)],
                      "boxes": window_boxes(win, line_boxes)}))
    return chunks
