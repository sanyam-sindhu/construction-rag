"""Tesseract OCR with our own reading-order pass.

Tesseract's page segmentation interleaves the two text columns of BIS standards
("given by the following: 26.5.1.3 Side face reinforcement"). We take word boxes
from TSV output, split any line that has a gap exactly at the page gutter, and emit
runs of column-lines left-column-first. Lines that genuinely cross the gutter
(headings, table rows like "Mild … 20") stay whole and act as region breaks.
"""

import os
import re
from collections import defaultdict

import pymupdf
import pytesseract
from PIL import Image

from .config import TESSDATA_DIR


def render(page: pymupdf.Page, dpi: int = 300) -> Image.Image:
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return Image.frombytes("L", (pix.width, pix.height), pix.samples)


def _tess_config(extra: str = "") -> str:
    return f'--tessdata-dir "{TESSDATA_DIR}" {extra}'.strip()


def ocr_lines(img: Image.Image, lang: str, psm: int = 3) -> list[dict]:
    data = pytesseract.image_to_data(img, lang=lang, config=_tess_config(f"--psm {psm}"),
                                     output_type=pytesseract.Output.DICT)
    groups = defaultdict(list)
    for i, txt in enumerate(data["text"]):
        if not txt.strip() or float(data["conf"][i]) < 0:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        groups[key].append({"x0": data["left"][i], "x1": data["left"][i] + data["width"][i],
                            "y0": data["top"][i], "y1": data["top"][i] + data["height"][i],
                            "text": txt, "conf": float(data["conf"][i])})
    lines = []
    for ws in groups.values():
        ws.sort(key=lambda w: w["x0"])
        lines.append({"words": ws, "y": min(w["y0"] for w in ws), "x0": ws[0]["x0"], "x1": ws[-1]["x1"]})
    lines.sort(key=lambda l: (l["y"], l["x0"]))
    return lines


def _split_at_gutter(line: dict, width: int) -> list[dict]:
    mid = width / 2
    ws = line["words"]
    for a, b in zip(ws, ws[1:]):
        if a["x1"] <= mid + 0.02 * width and mid - 0.01 * width <= b["x0"] <= mid + 0.07 * width and b["x0"] - a["x1"] > 0.012 * width:
            left = [w for w in ws if w["x0"] < b["x0"]]
            right = [w for w in ws if w["x0"] >= b["x0"]]
            return [_mk(left), _mk(right)]
    return [line]


def _mk(ws):
    return {"words": ws, "y": min(w["y0"] for w in ws), "x0": ws[0]["x0"], "x1": ws[-1]["x1"]}


def reading_order(lines: list[dict], width: int, two_column: bool = True) -> list[dict]:
    if not two_column:
        return lines
    mid = width / 2
    parts = []
    for ln in lines:
        parts.extend(_split_at_gutter(ln, width))
    out, region = [], []

    def flush():
        region.sort(key=lambda l: (l["x0"] >= mid, l["y"]))
        out.extend(region)
        region.clear()

    for ln in sorted(parts, key=lambda l: (l["y"], l["x0"])):
        crosses = ln["x0"] < mid - 0.02 * width and ln["x1"] > mid + 0.02 * width
        if crosses:
            flush()
            out.append(ln)
        else:
            region.append(ln)
    flush()
    return out


def line_text(line: dict) -> str:
    return " ".join(w["text"] for w in line["words"])


def ocr_number(img: Image.Image, box: tuple[int, int, int, int]) -> str:
    """Re-read a margin paragraph number ("5.1", "(ii)") with an English, whitelisted model."""
    x0, y0, x1, y1 = box
    crop = img.crop((max(0, x0 - 8), max(0, y0 - 8), x1 + 8, y1 + 8))
    txt = pytesseract.image_to_string(
        crop, lang="eng", config=_tess_config("--psm 7 -c tessedit_char_whitelist=0123456789.()ivxIVX"))
    return re.sub(r"\s+", "", txt)


def page_line_boxes(info: dict, dpi: int = 300) -> list[list[float]]:
    """PDF-point box for every cached OCR line; line height estimated from line spacing."""
    scale = 72 / dpi
    ys = sorted(l["y"] for l in info["lines"])
    gaps = sorted(b - a for a, b in zip(ys, ys[1:]) if 15 < b - a < 120)
    h = gaps[len(gaps) // 2] * 0.85 if gaps else 45
    return [[l["x0"] * scale, l["y"] * scale, l["x1"] * scale, (l["y"] + h) * scale] for l in info["lines"]]


def merge_boxes(boxes: list[list[float]], gap: float = 8) -> list[list[float]]:
    """Merge vertically adjacent, horizontally overlapping line boxes into highlight blocks."""
    out: list[list[float]] = []
    for b in sorted(boxes, key=lambda b: b[1]):
        for o in out:
            overlap = min(b[2], o[2]) - max(b[0], o[0])
            if -gap <= b[1] - o[3] <= gap and overlap > 0.3 * min(b[2] - b[0], o[2] - o[0]):
                o[:] = [min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])]
                break
        else:
            out.append(list(b))
    return [[round(v, 1) for v in o] for o in out]


def window_boxes(win, line_boxes: dict) -> dict[str, list]:
    """Highlight boxes per page for a window of (word, page, line_index) tuples."""
    by_page: dict[str, list] = {}
    for key in dict.fromkeys((p, li) for _, p, li in win):
        by_page.setdefault(str(key[0]), []).append(line_boxes[key[0]][key[1]])
    return {p: merge_boxes(bs) for p, bs in by_page.items()}


def _ocr_one(args):
    pdf_path, pno, lang, psm, two_column, margin_alt = args
    page = pymupdf.open(pdf_path)[pno - 1]
    img = render(page)
    lines = reading_order(ocr_lines(img, lang, psm), img.width, two_column)
    body_left = sorted(l["x0"] for l in lines)[len(lines) // 2] if lines else 0
    out = []
    for ln in lines:
        rec = {"text": line_text(ln), "x0": ln["x0"], "x1": ln["x1"], "y": ln["y"]}
        if margin_alt and ln["x0"] < body_left - 50:
            w = ln["words"][0]
            rec["alt"] = ocr_number(img, (w["x0"], w["y0"], w["x1"], w["y1"]))
        out.append(rec)
    return pno, {"width": img.width, "height": img.height, "lines": out}


def ocr_pdf(pdf_path, pages, cache_path, lang="eng", psm=3, two_column=False, margin_alt=False, workers=6):
    """OCR `pages` (1-based) once and cache line-level results as JSON."""
    import json
    from concurrent.futures import ProcessPoolExecutor

    if cache_path.exists():
        return {int(k): v for k, v in json.loads(cache_path.read_text(encoding="utf-8")).items()}
    jobs = [(str(pdf_path), p, lang, psm, two_column, margin_alt) for p in pages]
    with ProcessPoolExecutor(workers) as ex:
        result = dict(ex.map(_ocr_one, jobs))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result


os.environ.setdefault("OMP_THREAD_LIMIT", "1")  # we parallelise across pages instead
