"""Parser for the Rajasthan Housing Board Basic Schedule of Rates (BSR) 2024.

The BSR is an 824-page born-digital table: Item No. | Description | Unit | Rate.
Rows have no ruling lines, so generic table extractors merge the whole page into
one cell. Instead we read word coordinates, find the column x-positions from each
page's header row, and rebuild rows.

The important part is the hierarchy. A leaf such as

    1.5.2  Pipes, cables etc. exceeding 80mm dia but not exceeding 300mm dia   Mtr.  161.00

is meaningless without its parent "1.5 Excavating trenches of required width for
pipes, cables ..." (often on the previous page). Every rate row therefore becomes
one chunk whose text is the full ancestor chain + the row itself, so both the
retriever and the LLM see a self-contained item.
"""

import re
from dataclasses import dataclass, field

import pymupdf

from ..chunk import Chunk, split_words

DOC_ID = "bsr"

SECTIONS = {
    "G": "General Basic Rates",
    "B": "Building Work",
    "S": "Sanitary Work",
    "E": "Electric Work",
    "L": "Lift Work",
    "H": "Horticulture Work",
    "R": "Road Work",
    "M": "Misc. Circulars & Tables",
}

# Chapter titles transcribed from the section index pages (PDF pp. 10, 58, 239, 396, 638, 654).
# For B/S/E/H/R the first number of an item code is the chapter number.
CHAPTERS = {
    "B": ["Earth Work", "Mortar", "Concrete Work", "Reinforced Concrete Work", "Brick Work",
          "Stone Masonry", "Marble, Granite and Tile Work", "Wood Work", "Steel and Fencing Work",
          "Roofing", "Flooring Work", "Finishing Work", "Repair of Building",
          "Dismantling & Demolishing Work", "Water Proofing and Expansion Joint Treatment",
          "Aluminium & PVC Work", "Additional Miscellaneous Items", "Misc. Works"],
    "S": ["Sanitary Installation Work", "Water Supply Installation", "Drainage / Disposal Work",
          "Tube Wells, Open Wells & Hand Pumps", "Water Supply Work", "Sewer Line Work",
          "O&M Water Supply and Sewerage Work"],
    "E": ["Electrical Wiring in PVC Conduit", "Electrical Wiring in Steel Conduit",
          "Electrical Wiring in PVC Trunking", "Drawing of Wires and Sub Mains",
          "G.I./M.S./Wooden Boxes, Laminates & Dismantling", "Distribution Board & Accessories",
          "Electrical Accessories", "LT Panels & Accessories", "Air Circuit Breakers & MCCB",
          "Switch Fuse Unit, Change Over Switch & Bus Bar Chamber", "LT Cables",
          "LT Cable Termination & Accessories", "HT Cables & Termination Kits",
          "Earthing & Lightning Arrester", "Fans", "Storage Water Heaters", "Indoor Lighting",
          "Outdoor Lighting & Pole Tables", "Overhead Lines", "Local Area Networking",
          "Electrical Motor Pump Sets", "Air Cooling & Air Conditioning", "Substation Equipments",
          "Fire Protection Work", "Hire Charges for PA System & Temporary Lighting",
          "Repairing of Fans, Coolers, Pumps, Motors, Fridges & ACs", "Miscellaneous Items"],
    "H": ["Supply of Manure, Insecticides, Plants, Pots, T&P", "Maintenance of Gardens",
          "Development of Gardens", "Road Side Plantation"],
    "R": ["General Earthwork and Misc. Work", "Granular Sub-bases, Bases (Non-bituminous)",
          "Bases and Surface Courses (Bituminous)", "Cement Concrete Pavement", "Pipe Culverts",
          "Traffic Signs, Markings and Road Appurtenances", "Foundation and Superstructure",
          "Maintenance of Roads"],
}
# General Basic Rates use flat material codes, so chapter is decided by page label (G-n).
G_CHAPTERS = [(1, 1, "Hire Charges of Plants and Machinery"), (2, 2, "Labour"),
              (3, 41, "Materials"), (42, 43, "Carriage of Materials"), (44, 46, "Hire Charges of Tent")]

PAGE_LABEL_RE = re.compile(r"^([GBSELHRM])\s*-\s*(\d+)$")
DOTTED_CODE_RE = re.compile(r"^\d{1,2}(\.\d{1,3}){1,4}$")
FLAT_CODE_RE = re.compile(r"^\d{1,5}$")
RATE_RE = re.compile(r"^(Rs\.?\s*)?\d[\d,]*(\.\d+)?\s*%?$")
FOOTER_RE = re.compile(r"^RHB\s*BSR\s*-?\s*2024$", re.I)
NOTE_RE = re.compile(r"^note\b", re.I)
HEADER_WORDS = {"item", "code", "no.", "no", "description", "particulars", "unit", "rate", "rates", "(rs.)", "rs.)", "("}


@dataclass
class Record:
    section: str
    code: str
    page: int
    page_label: str
    lines: list = field(default_factory=list)  # (desc, unit, rate)
    bbox: list = field(default_factory=lambda: [1e9, 1e9, 0, 0])

    def extend(self, ws):
        self.bbox = [min(self.bbox[0], min(w[0] for w in ws)), min(self.bbox[1], min(w[1] for w in ws)),
                     max(self.bbox[2], max(w[2] for w in ws)), max(self.bbox[3], max(w[3] for w in ws))]

    @property
    def rates(self):
        return [ln for ln in self.lines if ln[2]]

    @property
    def text(self):
        return " ".join(ln[0] for ln in self.lines if ln[0]).strip()


def _lines(page):
    words = sorted(page.get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    lines = []
    for w in words:
        yc = (w[1] + w[3]) / 2
        if lines and abs(lines[-1][0] - yc) <= 3.0:
            lines[-1][1].append(w)
        else:
            lines.append([yc, [w]])
    return [(yc, sorted(ws, key=lambda w: w[0])) for yc, ws in lines]


def _page_label(page):
    for line in page.get_text().splitlines()[:4]:
        m = PAGE_LABEL_RE.match(line.strip())
        if m:
            return m.group(1), int(m.group(2)), f"{m.group(1)}-{m.group(2)}"
    return None, None, None


def _zones(page):
    """Column boundaries from the header row (Item/Code … Unit … Rate)."""
    words = [w for w in page.get_text("words") if w[1] < 200]
    item = [w for w in words if w[4].lower() in ("item", "code")]
    unit = [w for w in words if w[4].lower() == "unit"]
    if not item or not unit:
        return None
    unit_x = unit[0][0]
    rate = [w for w in words if w[4].lower().strip("(") in ("rate", "rates", "rs.)") and w[0] > unit_x]
    if not rate:
        return None
    header_bottom = max(w[3] for w in item + unit + rate)
    return {
        "code_max": item[0][0] + 30,
        "unit_min": unit_x - 20,
        "rate_min": min(w[0] for w in rate) - 15,
        "header_bottom": header_bottom + 1,
    }


def _chapter(section, code, label_num):
    if section == "G":
        for lo, hi, name in G_CHAPTERS:
            if lo <= (label_num or 0) <= hi:
                return name
        return ""
    names = CHAPTERS.get(section)
    if not names or not code or not code.split(".")[0].isdigit():
        return ""
    n = int(code.split(".")[0])
    return names[n - 1] if 1 <= n <= len(names) else ""


def _clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\s+([,.;:)])", r"\1", s)


def parse(pdf_path) -> list[Chunk]:
    doc = pymupdf.open(pdf_path)
    records: list[Record] = []
    notes: list[Chunk] = []
    page_texts: list[Chunk] = []
    zones = None
    last_section = None

    for pno in range(doc.page_count):
        page = doc[pno]
        raw = page.get_text()
        if len(raw.strip()) < 40:
            continue
        section, label_num, label = _page_label(page)
        z = _zones(page)
        if section is None or section == "M" or z is None:
            # Front matter, misc circulars and reference tables: plain page chunks.
            if section is not None and z is None and section != "M" and zones is not None and section == last_section:
                z = zones  # continuation page without a repeated header
            else:
                body = _clean(" ".join(ln for ln in raw.splitlines() if not FOOTER_RE.match(ln.strip())))
                sec_name = SECTIONS.get(section, "Front matter")
                for i, part in enumerate(split_words(body)):
                    page_texts.append(Chunk(
                        id=f"bsr-p{pno + 1}-{i}", doc_id=DOC_ID, page=pno + 1, page_label=label or str(pno + 1),
                        ref=f"Page {label or pno + 1}", section=f"RHB BSR 2024 › {sec_name}", text=part,
                        meta={"type": "page"}))
                continue
        zones, last_section = z, section
        code_re = FLAT_CODE_RE if section == "G" else DOTTED_CODE_RE
        current: Record | None = None
        in_note = False
        note_lines: list[str] = []

        for _yc, ws in _lines(page):
            if ws[0][1] < z["header_bottom"]:
                continue
            text_all = " ".join(w[4] for w in ws)
            if FOOTER_RE.match(text_all) or PAGE_LABEL_RE.match(text_all):
                continue
            if all(w[4].lower() in HEADER_WORDS for w in ws):
                continue
            first = ws[0]
            is_code = first[0] < z["code_max"] and code_re.match(first[4])
            if NOTE_RE.match(first[4]) and not is_code:
                in_note = True
            if in_note and not (is_code and section != "G"):
                note_lines.append(text_all)
                continue
            in_note = False
            if is_code:
                current = Record(section, first[4], pno + 1, label)
                records.append(current)
            if current is None:
                note_lines.append(text_all)
                continue
            current.extend(ws)
            if is_code:
                ws = ws[1:]
            desc = " ".join(w[4] for w in ws if w[0] < z["unit_min"])
            unit = " ".join(w[4] for w in ws if z["unit_min"] <= w[0] < z["rate_min"])
            rate = " ".join(w[4] for w in ws if w[0] >= z["rate_min"])
            if rate and not RATE_RE.match(rate):
                desc, rate = f"{desc} {unit} {rate}".strip(), ""
                unit = ""
            current.lines.append((desc, unit, rate))

        if note_lines:
            chap = _chapter(section, current.code if current else None, label_num)
            notes.append(Chunk(
                id=f"bsr-notes-p{pno + 1}", doc_id=DOC_ID, page=pno + 1, page_label=label,
                ref=f"Notes, page {label}", section=" › ".join(filter(None, ["RHB BSR 2024", SECTIONS[section], chap])),
                text=_clean(" ".join(note_lines)), meta={"type": "notes"}))

    return _records_to_chunks(records) + notes + page_texts


def _records_to_chunks(records: list[Record]) -> list[Chunk]:
    by_code: dict[tuple, Record] = {}
    for r in records:
        by_code.setdefault((r.section, r.code), r)

    def ancestors(r: Record) -> list[str]:
        parts = r.code.split(".")
        out = []
        for i in range(2, len(parts)):
            p = by_code.get((r.section, ".".join(parts[:i])))
            if p is not None and p is not r and p.text:
                out.append(_clean(p.text))
        return out

    parent_codes = {".".join(r.code.split(".")[:i]) for r in records for i in range(2, len(r.code.split(".")))}
    chunks, seen = [], set()
    for r in records:
        rates = r.rates
        label_num = int(r.page_label.split("-")[1]) if r.page_label else None
        chap = _chapter(r.section, r.code, label_num)
        section = " › ".join(filter(None, ["RHB BSR 2024", SECTIONS[r.section], chap]))
        if not rates and (r.code in parent_codes or not r.text):
            continue  # headings live on inside their children's text

        chain = ancestors(r)
        prefix = "Material/labour code" if r.section == "G" else "Item"
        head = f"{prefix} {r.section}-{r.code}: "
        # Distinguishing text first (sub-heading › leaf, rate), the long shared parent
        # description after: siblings then differ in their first tokens, which helps the
        # embedder (512-token cap), the LLM, and a human scanning source cards.
        specific, general = (chain[1:], chain[0]) if chain else ([], "")
        footer = (f"\nUnder: {general}" if general else "") + f"\nSection: {section.removeprefix('RHB BSR 2024 › ')}"
        if len(rates) <= 1:
            desc = _clean(r.text)
            unit, rate = (rates[0][1], rates[0][2]) if rates else ("", "")
            text = head + " › ".join(specific + [desc])
            if rate:
                text += f"\nUnit: {unit or '-'} | " + (f"Rate: {rate} extra" if rate.endswith("%") else f"Rate: Rs. {rate}")
            text += footer
        else:
            # Several rate rows under one code, often with nested sub-labels ("I. Ordinary soil
            # (i) up to 3 m … 453.00 (ii) 3 m to 6 m … 512.00"). Splitting them reliably needs
            # layout cues we don't have, so keep the record whole, rows in source order.
            rows, buf = [], []
            for d, u, rt in r.lines:
                buf.append(d)
                if rt:
                    rows.append(f"{_clean(' '.join(buf))} → {u or '-'}: " + (rt if rt.endswith("%") else f"Rs. {rt}"))
                    buf = []
            if any(buf):
                rows.append(_clean(" ".join(buf)))
            desc = "\n".join(rows)
            unit, rate = rates[0][1], "; ".join(rt for _, _, rt in rates)
            text = head + (" › ".join(specific) + " ›\n" if specific else "\n") + desc + footer

        cid = f"bsr-{r.section}-{r.code}"
        if cid in seen:
            cid = f"{cid}-p{r.page}"
        seen.add(cid)
        chunks.append(Chunk(
            id=cid, doc_id=DOC_ID, page=r.page, page_label=r.page_label,
            ref=f"Item {r.section}-{r.code}", section=section, text=text,
            meta={"type": "item", "code": r.code, "unit": unit, "rate": rate, "desc": desc,
                  "parents": chain, "n_rates": len(rates),
                  "boxes": {str(r.page): [[round(v, 1) for v in r.bbox]]}}))
    return chunks
