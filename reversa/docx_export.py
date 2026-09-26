"""Word export: Reversa's Markdown artifacts -> a clean, navigable .docx.

Layout
  * title page (title, units, source, backend, confidence index — read from the artifacts)
  * Contents: a real Word TOC field (levels 1-2) with clickable entries; Word refreshes it
    on open. If LibreOffice (`soffice`) and `pdftotext` are installed, page numbers are
    filled in up front so other viewers show them too.
  * one numbered section per artifact file (1, 1.1, 1.1.1), each starting on a new page
  * running header, "Page X of Y" footer (none on the title page)
  * tables sized to their content, repeating header rows, banded rows; text-heavy tables
    become one block per row; tables with 7+ columns get a landscape page
  * empty tables read "None recorded."

Content is not rewritten: only the file-name structure is replaced by numbered sections,
plus three clearer section titles (see RENAME).

    from reversa.docx_export import build_docx, ordered_markdown_files
    build_docx(sdd_dir, "reversa_spec.docx", title="Operational Specification")

Needs only pypandoc (with a pandoc binary, e.g. pypandoc_binary) to read the Markdown; the
.docx itself is written with the standard library, so there is no Word library to install.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from xml.sax.saxutils import escape as _xml_escape
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Reading order for artifact files; anything else follows alphabetically.
ORDER = ["README.md", "ops_spec.md", "rules.md", "gaps_contradictions.md", "process_flow.md",
         "processes.md", "process.md", "inventory.md", "architecture.md", "migration.md", "risks.md",
         "gaps.md", "questions.md", "comparison.md"]
RENAME = {"Reversa operational specification": "About this document",
          "Process": "Process flow",
          "Gaps": "Gap register"}

_BAD_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")

# ---- design tokens (twips / hex) ----------------------------------------------------
A4_W, A4_H = 11906, 16838
MARGIN = dict(top=1440, bottom=1300, left=1440, right=1440, header=600, footer=600)
PORTRAIT_W = A4_W - MARGIN["left"] - MARGIN["right"]          # 9026
LANDSCAPE_W = A4_H - MARGIN["left"] - MARGIN["right"]         # 13958
NAVY, BLUE, INK, GREY, RULE = "1F3864", "2E5597", "262626", "6B7280", "BFC7D5"
CARD_BG, BAND, CODE_BG = "F5F7FB", "F2F5FA", "F3F4F6"
# Fonts installed on both macOS and Windows (Calibri/Consolas are missing on Macs without Office)
FONT, MONO = "Arial", "Courier New"


def ordered_markdown_files(sdd: Path) -> list[Path]:
    return sorted(Path(sdd).rglob("*.md"),
                  key=lambda p: (ORDER.index(p.name) if p.name in ORDER else len(ORDER),
                                 str(p.relative_to(sdd))))


# =====================================================================================
# 1. Markdown -> intermediate representation
# =====================================================================================
@dataclass
class Meta:
    title: str
    units: str = ""
    source: str = ""
    backend: str = ""
    stack: str = ""
    confidence: str = ""
    headings: list[dict] = field(default_factory=list)


def _pandoc_blocks(markdown: str) -> list[dict]:
    import pypandoc
    return json.loads(pypandoc.convert_text(markdown, "json", format="gfm"))["blocks"]


def _runs(xs: list[dict], b: bool = False, i: bool = False) -> list[dict]:
    out: list[dict] = []
    for x in xs:
        t, c = x["t"], x.get("c")
        if t == "Str":
            out.append({"t": c, "b": b, "i": i})
        elif t in ("Space", "SoftBreak"):
            out.append({"t": " ", "b": b, "i": i})
        elif t == "LineBreak":
            out.append({"br": True})
        elif t == "Code":
            out.append({"t": c[1], "code": True, "b": b, "i": i})
        elif t == "Strong":
            out += _runs(c, True, i)
        elif t == "Emph":
            out += _runs(c, b, True)
        elif t in ("Strikeout", "Underline", "SmallCaps", "Superscript", "Subscript"):
            out += _runs(c, b, i)
        elif t in ("Link", "Span"):
            out += _runs(c[1], b, i)
        elif t == "Image":
            out += _runs(c[1], b, i)
        elif t == "Quoted":
            q = "\u2018\u2019" if c[0]["t"] == "SingleQuote" else "\u201c\u201d"
            out += [{"t": q[0], "b": b, "i": i}] + _runs(c[1], b, i) + [{"t": q[1], "b": b, "i": i}]
        elif t == "RawInline" and re.fullmatch(r"<br\s*/?>", c[1].strip(), re.I):
            out.append({"br": True})
        elif t == "Math":
            out.append({"t": c[1], "b": b, "i": i})
    return _merge(out)


def _merge(rs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for r in rs:
        if out and "t" in r and "t" in out[-1] and \
                all(out[-1].get(k) == r.get(k) for k in ("b", "i", "code")):
            out[-1] = dict(out[-1], t=out[-1]["t"] + r["t"])
        else:
            out.append(dict(r))
    while out and (out[0].get("br") or out[0].get("t", "x").strip() == ""):
        out.pop(0)
    while out and (out[-1].get("br") or out[-1].get("t", "x").strip() == ""):
        out.pop()
    return out


def _plain(rs: list[dict]) -> str:
    return "".join(r.get("t", " ") for r in rs)


def _cell_runs(bs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for b in bs:
        if b["t"] in ("Plain", "Para"):
            r = _runs(b["c"])
        elif b["t"] == "BulletList":
            r = []
            for item in b["c"]:
                r += [{"t": "\u2022 "}] + _cell_runs(item) + [{"br": True}]
            r = _merge(r)
        else:
            r = []
        if r:
            if out:
                out.append({"br": True})
            out += r
    return out


def _table(c: list) -> dict:
    colspecs, head, bodies = c[2], c[3], c[4]
    header = [_cell_runs(cell[4]) for row in head[1] for cell in row[1]]
    rows = [[_cell_runs(cell[4]) for cell in r[1]] for bd in bodies for r in bd[3]]
    ncol = len(colspecs)
    header += [[] for _ in range(ncol - len(header))]
    rows = [r + [[] for _ in range(ncol - len(r))] for r in rows]
    if not rows:
        return {"type": "empty", "text": "None recorded."}
    avg = [sum(len(_plain(r[k])) for r in rows) / len(rows) for k in range(ncol)]
    hdr_txt = [_plain(h) for h in header]
    if ncol >= 2 and (max(avg) > 250 or (ncol >= 6 and max(avg) > 150)):
        short = [k for k in range(1, ncol) if avg[k] < 45]
        long_ = [k for k in range(1, ncol) if avg[k] >= 45]
        return {"type": "cards", "items": [
            {"title": r[0],
             "meta": [[hdr_txt[k], r[k]] for k in short if _plain(r[k]).strip()],
             "body": [[hdr_txt[k], r[k]] for k in long_ if _plain(r[k]).strip()]} for r in rows]}
    landscape = ncol >= 7
    width = LANDSCAPE_W if landscape else PORTRAIT_W
    numeric = [all(re.fullmatch(r"[\d.,%\s-]*", _plain(r[k])) for r in rows) and
               any(_plain(r[k]).strip() for r in rows) for k in range(ncol)]
    return {"type": "table", "header": header, "rows": rows, "landscape": landscape,
            "width": width, "widths": _widths(hdr_txt, rows, avg, width), "numeric": numeric}


def _widths(hdr: list[str], rows: list[list[dict]], avg: list[float], total: int) -> list[int]:
    def longest_word(s: str) -> int:
        return max((len(w) for w in s.split()), default=1)
    mins = [max(600, min(max([longest_word(hdr[k])] + [longest_word(_plain(r[k])) for r in rows]), 14)
                * 95 + 220) for k in range(len(hdr))]
    if sum(mins) >= total:
        ws = mins
    else:
        weight = [max(a, 1) ** 0.85 for a in avg]
        extra = total - sum(mins)
        ws = [m + extra * w / sum(weight) for m, w in zip(mins, weight)]
    out = [int(w * total / sum(ws)) for w in ws]
    out[-1] += total - sum(out)
    return out


def _blocks(bs: list[dict]) -> list[dict]:
    res: list[dict] = []
    for b in bs:
        t, c = b["t"], b.get("c")
        if t in ("Para", "Plain"):
            r = _runs(c)
            if not r:
                continue
            first = r[0]
            card = bool(first.get("b") and re.match(r"(BR|DT|GC|Q|P|REQ|T)-\d+", first.get("t", ""))
                        and any(x.get("br") for x in r))
            res.append({"type": "p", "runs": r, "card": card})
        elif t == "BulletList":
            res.append({"type": "list", "ordered": False, "items": [_blocks(it) for it in c]})
        elif t == "OrderedList":
            res.append({"type": "list", "ordered": True, "items": [_blocks(it) for it in c[1]]})
        elif t == "Table":
            res.append(_table(c))
        elif t == "CodeBlock":
            res.append({"type": "code", "text": c[1]})
        elif t in ("BlockQuote",):
            res += _blocks(c)
        elif t == "Div":
            res += _blocks(c[1])
        elif t == "Header":
            txt = _plain(_runs(c[2])).strip()
            res.append({"type": "h", "level": c[0], "text": txt})
        elif t == "RawBlock" and c[0] == "html":
            m = re.search(r"<summary>(.*?)</summary>", c[1], re.S | re.I)
            if m:
                res.append({"type": "label", "text": re.sub(r"<[^>]+>", "", m.group(1)).strip()})
            else:
                txt = re.sub(r"<[^>]+>", " ", c[1]).strip()
                if txt:
                    res.append({"type": "p", "runs": [{"t": txt}], "card": False})
        elif t == "HorizontalRule":
            continue
    return res


def _pretty(rel: str) -> str:
    s = rel[:-3] if rel.endswith(".md") else rel
    s = " \u203a ".join(part.replace("_", " ").replace("-", " ") for part in s.split("/"))
    return s[:1].upper() + s[1:]


def to_ir(files: Iterable[tuple[str, str]], title: str) -> tuple[list[dict], Meta]:
    """files: (relative path, markdown text) in reading order."""
    meta = Meta(title=title)
    ir: list[dict] = []
    counters = [0, 0, 0]
    for rel, text in files:
        blocks = _blocks(_pandoc_blocks(text))
        if not blocks:
            continue
        if not (blocks[0]["type"] == "h" and blocks[0]["level"] == 1):
            blocks.insert(0, {"type": "h", "level": 1, "text": _pretty(rel)})
        for b in blocks:
            if b["type"] == "p":
                _harvest_meta(meta, _plain(b["runs"]))
            if b["type"] != "h":
                ir.append(b)
                continue
            level = min(b["level"], 4)
            text = b["text"].replace("---", "\u2014")
            if level == 1:
                text = RENAME.get(text, text)
            num = ""
            if level <= 3:
                counters[level - 1] += 1
                for k in range(level, 3):
                    counters[k] = 0
                num = ".".join(str(n) for n in counters[:level])
            h = {"type": "h", "level": level, "num": num, "text": text,
                 "id": f"_Toc{len(meta.headings) + 1:04d}"}
            meta.headings.append(h)
            ir.append(h)
    return ir, meta


def _harvest_meta(meta: Meta, s: str) -> None:
    m = re.search(r"Generated by Reversa for (\S+) \(backend: ([\w-]+)\)", s)
    if m and not meta.source:
        meta.source, meta.backend = m.group(1), m.group(2)
    m = re.search(r"confidence index:\s*([\d.]+%\s*over\s*\d+\s*claims)", s, re.I)
    if m and not meta.confidence:
        meta.confidence = m.group(1)
    m = re.match(r"Units:\s*(.+)$", s.strip())
    if m and not meta.units:
        meta.units = m.group(1).strip()
    m = re.search(r"Stack:\s*([^\n]+?)(?:\s+Files:|$)", s)
    if m and not meta.stack:
        meta.stack = m.group(1).strip()


# =====================================================================================
# 2. IR -> .docx (standard library: zipfile + OOXML strings, written in schema order)
# =====================================================================================
def _x(s: str) -> str:
    """Escape text for XML and drop characters XML 1.0 forbids."""
    return _xml_escape(_BAD_XML.sub("", s), {'"': "&quot;"})


def _rpr(*, font: str | None = None, b=False, i=False, color: str | None = None,
         spacing: int | None = None, size: float | None = None, shade: str | None = None) -> str:
    parts = []
    if font:
        parts.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}"/>')
    if b:
        parts.append("<w:b/><w:bCs/>")
    if i:
        parts.append("<w:i/><w:iCs/>")
    if color:
        parts.append(f'<w:color w:val="{color}"/>')
    if spacing:
        parts.append(f'<w:spacing w:val="{spacing}"/>')
    if size:
        hp = int(round(size * 2))
        parts.append(f'<w:sz w:val="{hp}"/><w:szCs w:val="{hp}"/>')
    if shade:
        parts.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
    return f"<w:rPr>{''.join(parts)}</w:rPr>" if parts else ""


def _run(text: str, **fmt) -> str:
    return f'<w:r>{_rpr(**fmt)}<w:t xml:space="preserve">{_x(text)}</w:t></w:r>'


def _ppr(*, style: str | None = None, keep_next=False, keep_lines=False, page_break=False,
         num: tuple[int, int] | None = None, borders: dict[str, tuple[int, str, int]] | None = None,
         shade: str | None = None, tabs: list[tuple[str, int, str | None]] | None = None,
         before: float | None = None, after: float | None = None, line: float | None = None,
         left: int | None = None, right: int | None = None, hanging: int | None = None,
         jc: str | None = None, outline: int | None = None, sect: str = "") -> str:
    """Paragraph properties, emitted in the order the OOXML schema requires."""
    p = []
    if style:
        p.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        p.append("<w:keepNext/>")
    if keep_lines:
        p.append("<w:keepLines/>")
    if page_break:
        p.append("<w:pageBreakBefore/>")
    if num:
        p.append(f'<w:numPr><w:ilvl w:val="{num[1]}"/><w:numId w:val="{num[0]}"/></w:numPr>')
    if borders:
        p.append("<w:pBdr>" + "".join(
            f'<w:{side} w:val="single" w:sz="{sz}" w:space="{sp}" w:color="{col}"/>'
            for side in ("top", "left", "bottom", "right") if side in borders
            for sz, col, sp in [borders[side]]) + "</w:pBdr>")
    if shade:
        p.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
    if tabs:
        p.append("<w:tabs>" + "".join(
            f'<w:tab w:val="{kind}"' + (f' w:leader="{leader}"' if leader else "") + f' w:pos="{pos}"/>'
            for kind, pos, leader in tabs) + "</w:tabs>")
    if before is not None or after is not None or line is not None:
        a = ""
        if before is not None:
            a += f' w:before="{int(before * 20)}"'
        if after is not None:
            a += f' w:after="{int(after * 20)}"'
        if line is not None:
            a += f' w:line="{int(line * 240)}" w:lineRule="auto"'
        p.append(f"<w:spacing{a}/>")
    if left is not None or right is not None or hanging is not None:
        a = ""
        if left is not None:
            a += f' w:left="{left}"'
        if right is not None:
            a += f' w:right="{right}"'
        if hanging is not None:
            a += f' w:hanging="{hanging}"'
        p.append(f"<w:ind{a}/>")
    if jc:
        p.append(f'<w:jc w:val="{jc}"/>')
    if outline is not None:
        p.append(f'<w:outlineLvl w:val="{outline}"/>')
    p.append(sect)
    body = "".join(p)
    return f"<w:pPr>{body}</w:pPr>" if body else ""


def _fld(instr: str, **fmt) -> str:
    rp = _rpr(**fmt)
    return (f'<w:r>{rp}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{rp}<w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
            f'<w:r>{rp}<w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{rp}<w:t>1</w:t></w:r>'
            f'<w:r>{rp}<w:fldChar w:fldCharType="end"/></w:r>')


def _render(ir: list[dict], meta: Meta, out: Path, pages: dict[str, int | str] | None) -> None:
    """Write the .docx with the standard library only (zipfile + OOXML strings)."""
    body: list[str] = []
    P = body.append
    num_defs: list[int] = []                         # one <w:num> per ordered list (restart at 1)

    def runs(rs, *, size=None, color=None, bold=False, italic=False) -> str:
        out_, brk = [], False
        for r in rs or []:
            if r.get("br"):
                brk = True
                continue
            fmt = dict(b=bool(r.get("b") or bold), i=bool(r.get("i") or italic), color=color, size=size)
            if r.get("code"):
                fmt.update(font=MONO, size=(size or 10.5) - 1.5, color="24292F", shade=CODE_BG)
            rp = _rpr(**fmt)
            out_.append(f"<w:r>{rp}{'<w:br/>' if brk else ''}"
                        f'<w:t xml:space="preserve">{_x(r["t"])}</w:t></w:r>')
            brk = False
        return "".join(out_)

    # ---- title page -----------------------------------------------------------------------
    P(f'<w:p>{_ppr(before=170, after=6)}{_run("REVERSE-ENGINEERED SPECIFICATION", b=True, size=10, color=BLUE, spacing=40)}</w:p>')
    P(f'<w:p>{_ppr(after=10, line=1.0)}{_run(meta.title, b=True, size=30, color=NAVY)}</w:p>')
    P(f'<w:p>{_ppr(after=30, borders={"bottom": (12, BLUE, 12)})}'
      f'{_run(meta.units or "Legacy system", size=16, color=BLUE)}</w:p>')
    facts = [("System", meta.units + (f" ({meta.stack})" if meta.stack else "")) if meta.units else None,
             ("Source", meta.source) if meta.source else None,
             ("Generated by", "Reversa" + (f" \u00b7 {meta.backend} backend" if meta.backend else "")),
             ("Confidence index", meta.confidence) if meta.confidence else None]
    for f in filter(None, facts):
        P(f'<w:p>{_ppr(tabs=[("left", 2200, None)], after=3)}{_run(f[0], size=10, color=GREY)}'
          f'<w:r>{_rpr(size=10)}<w:tab/><w:t xml:space="preserve">{_x(f[1])}</w:t></w:r></w:p>')
    P(f'<w:p>{_ppr(before=120, after=0)}'
      f'{_run("Every statement is marked confirmed (cites code), inferred (a hypothesis) or gap (not yet known). Confirm the rules with the system owner before relying on them.", i=True, size=9.5, color=GREY)}</w:p>')

    # ---- contents (TOC field; cached entries are clickable, page numbers when known) --------
    P(f'<w:p>{_ppr(page_break=True, after=15, borders={"bottom": (8, BLUE, 6)})}'
      f'{_run("Contents", b=True, size=18, color=NAVY)}</w:p>')
    toc = [h for h in meta.headings if h["level"] <= 2]
    for k, h in enumerate(toc):
        label = (h["num"] + "\u2003" if h["num"] else "") + h["text"]
        begin = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                 '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
                 '<w:r><w:fldChar w:fldCharType="separate"/></w:r>') if k == 0 else ""
        page = ""
        if pages is not None and h["id"] in pages:
            page = f'<w:r><w:tab/><w:t>{_x(str(pages[h["id"]]))}</w:t></w:r>'
        end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if k == len(toc) - 1 else ""
        P(f'<w:p>{_ppr(style="TOC1" if h["level"] == 1 else "TOC2")}{begin}'
          f'<w:hyperlink w:anchor="{h["id"]}" w:history="1">'
          f'<w:r><w:t xml:space="preserve">{_x(label)}</w:t></w:r>{page}</w:hyperlink>{end}</w:p>')

    # ---- body -------------------------------------------------------------------------------
    bm = [0]

    def heading(h, first_on_page: bool) -> None:
        bm[0] += 1
        label = (h["num"] + "\u2003" if h["num"] else "") + h["text"]
        pb = h["level"] == 1 and not first_on_page
        style = "Heading%d" % h["level"]
        P(f'<w:p>{_ppr(style=style, page_break=pb)}'
          f'<w:bookmarkStart w:id="{bm[0]}" w:name="{h["id"]}"/>'
          f'<w:r><w:t xml:space="preserve">{_x(label)}</w:t></w:r><w:bookmarkEnd w:id="{bm[0]}"/></w:p>')

    def lst(b, level: int = 0) -> None:
        lvl = min(level, 2)
        if b["ordered"]:
            num_defs.append(len(num_defs) + 2)       # numId 1 = bullets; 2.. = ordered lists
            num_id = num_defs[-1]
        else:
            num_id = 1
        for item in b["items"]:
            first = True
            for blk in item:
                if blk["type"] == "p" and first:
                    P(f'<w:p>{_ppr(num=(num_id, lvl), after=3)}{runs(blk["runs"])}</w:p>')
                    first = False
                elif blk["type"] == "list":
                    lst(blk, level + 1)
                else:
                    block(blk)

    def table(t) -> None:
        rows, widths = t["rows"], t["widths"]
        keep = len(rows) <= 12
        border = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="{RULE}"/>'
                         for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
        x = [f'<w:tbl><w:tblPr><w:tblW w:w="{t["width"]}" w:type="dxa"/><w:tblBorders>{border}</w:tblBorders>'
             '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="70" w:type="dxa"/>'
             '<w:left w:w="110" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/>'
             '<w:right w:w="110" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
             + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]
        for ri, data in enumerate([t["header"]] + rows):
            x.append("<w:tr><w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if ri == 0 else "") + "</w:trPr>")
            for k, cell in enumerate(data):
                fill = NAVY if ri == 0 else (BAND if ri % 2 == 0 else None)
                shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
                ppr = _ppr(keep_next=ri == 0 or (keep and ri < len(rows)), after=0, line=1.05,
                           jc="right" if t["numeric"][k] else None)
                content = (runs(cell, size=9, color="FFFFFF", bold=True) if ri == 0
                           else runs(cell, size=9))
                x.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[k]}" w:type="dxa"/>{shd}</w:tcPr>'
                         f"<w:p>{ppr}{content}</w:p></w:tc>")
            x.append("</w:tr>")
        x.append("</w:tbl>")
        P("".join(x))
        P(f'<w:p>{_ppr(after=4)}</w:p>')

    card_bdr = {"left": (18, BLUE, 8)}

    def card_para(content: str, keep_next=True, before=0.0, line=1.1) -> None:
        P(f'<w:p>{_ppr(keep_next=keep_next, keep_lines=True, borders=card_bdr, shade=CARD_BG, before=before, after=0, line=line, left=140, right=140)}{content}</w:p>')

    def card_end() -> None:
        card_para("", keep_next=False, line=0.45)
        P(f'<w:p>{_ppr(after=0, line=0.7)}</w:p>')

    def cards(c) -> None:
        for it in c["items"]:
            head = runs(it["title"], size=11, color=NAVY, bold=True)
            for k, (label, v) in enumerate(it["meta"]):
                head += _run(("   \u00b7   " if k else "   ") + label + ": ", size=9, color=GREY)
                head += runs(v, size=9, color="404040")
            card_para(head)
            for label, v in it["body"]:
                card_para(_run(label, b=True, size=9.5, color=BLUE) + "<w:r><w:br/></w:r>" + runs(v), before=4)
            card_end()

    def block(b, first_on_page: bool = False) -> None:
        t = b["type"]
        if t == "h":
            heading(b, first_on_page)
        elif t == "p":
            if b["card"]:
                card_para(runs(b["runs"]))
                card_end()
            else:
                P(f"<w:p>{runs(b['runs'])}</w:p>")
        elif t == "list":
            lst(b)
        elif t == "table":
            table(b)
        elif t == "cards":
            cards(b)
        elif t == "empty":
            P(f'<w:p>{_run(b["text"], i=True, color=GREY)}</w:p>')
        elif t == "label":
            P(f'<w:p>{_ppr(keep_next=True)}{_run(b["text"], b=True, size=10, color=BLUE)}</w:p>')
        elif t == "code":
            lines = b["text"].split("\n")
            for k, line in enumerate(lines):
                P(f'<w:p>{_ppr(keep_next=k < len(lines) - 1, borders={"left": (12, RULE, 8)}, shade=CODE_BG, before=3 if k == 0 else 0, after=0, line=1.0, left=140)}'
                  f'{_run(line or " ", font=MONO, size=9)}</w:p>')
            P(f'<w:p>{_ppr(after=0)}</w:p>')

    def sect_pr(landscape: bool, title_page: bool = False) -> str:
        w, h = (A4_H, A4_W) if landscape else (A4_W, A4_H)
        m = MARGIN
        refs = ('<w:headerReference w:type="default" r:id="rIdHeader"/>'
                + ('<w:headerReference w:type="first" r:id="rIdHeaderFirst"/>' if title_page else "")
                + '<w:footerReference w:type="default" r:id="rIdFooter"/>'
                + ('<w:footerReference w:type="first" r:id="rIdFooterFirst"/>' if title_page else ""))
        return (f"<w:sectPr>{refs}<w:type w:val=\"nextPage\"/>"
                f'<w:pgSz w:w="{w}" w:h="{h}"' + (' w:orient="landscape"' if landscape else "") + "/>"
                f'<w:pgMar w:top="{m["top"]}" w:right="{m["right"]}" w:bottom="{m["bottom"]}" '
                f'w:left="{m["left"]}" w:header="{m["header"]}" w:footer="{m["footer"]}" w:gutter="0"/>'
                + ("<w:titlePg/>" if title_page else "") + "</w:sectPr>")

    def end_section(landscape: bool, title_page: bool) -> None:
        # the section's properties ride on a tiny empty paragraph that closes it
        P(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
          f"{_rpr(size=1)}{sect_pr(landscape, title_page)}</w:pPr></w:p>")

    land: set[int] = set()
    for i, b in enumerate(ir):
        if b["type"] == "table" and b["landscape"]:
            s = i
            while s > 0 and ir[s]["type"] != "h":
                s -= 1
            land.update(range(s, i + 1))
    current, first_section, first_on_page = False, True, False
    for i, b in enumerate(ir):
        want = i in land
        if want != current:
            end_section(current, title_page=first_section)
            first_section, current, first_on_page = False, want, True
        block(b, first_on_page)
        first_on_page = False
    final_sect = sect_pr(current, title_page=first_section)

    # ---- package parts ------------------------------------------------------------------------
    W = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
         'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
    HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    document = f"{HEAD}<w:document {W}><w:body>{''.join(body)}{final_sect}</w:body></w:document>"

    def pstyle(sid, name, *, ppr="", rpr="", based="Normal", nxt="Normal", extra=""):
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/>'
                f'<w:basedOn w:val="{based}"/><w:next w:val="{nxt}"/>{extra}{ppr}{rpr}</w:style>')

    heads = {1: (18, NAVY, 0, 12), 2: (14, BLUE, 18, 7), 3: (11.5, NAVY, 13, 5), 4: (10.5, "404040", 10, 4)}
    styles = (
        f'{HEAD}<w:styles {W}><w:docDefaults><w:rPrDefault>{_rpr(font=FONT, size=10.5, color=INK)}'
        f'</w:rPrDefault><w:pPrDefault>{_ppr(after=6, line=1.15)}</w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
        + "".join(pstyle(f"Heading{n}", f"heading {n}", extra="<w:uiPriority w:val=\"9\"/><w:qFormat/>",
                         ppr=_ppr(keep_next=True, before=bf, after=af, line=1.1, outline=n - 1,
                                  borders={"bottom": (8, BLUE, 6)} if n == 1 else None),
                         rpr=_rpr(font=FONT, b=True, i=n == 4, color=col, size=sz))
                  for n, (sz, col, bf, af) in heads.items())
        + pstyle("TOC1", "toc 1", ppr=_ppr(tabs=[("right", PORTRAIT_W, "dot")], before=7, after=2),
                 rpr=_rpr(b=True, color=NAVY, size=10.5))
        + pstyle("TOC2", "toc 2", ppr=_ppr(tabs=[("right", PORTRAIT_W, "dot")], before=0, after=2, left=440),
                 rpr=_rpr(color=INK, size=10))
        + '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/></w:style>'
        + '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/>'
          '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/>'
          '<w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/>'
          '</w:tblCellMar></w:tblPr></w:style>'
        + "</w:styles>")

    def levels(bullet: bool) -> str:
        out_ = []
        for l in range(3):
            fmt, text = (("bullet", ["\u2022", "\u2013", "\u25e6"][l]) if bullet
                         else (["decimal", "lowerLetter", "lowerRoman"][l], f"%{l + 1}."))
            ind = (360 + 360 * l, 260) if bullet else (460 + 360 * l, 400)
            out_.append(f'<w:lvl w:ilvl="{l}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
                        f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="left"/>'
                        f'<w:pPr><w:ind w:left="{ind[0]}" w:hanging="{ind[1]}"/></w:pPr>'
                        + (_rpr(font=FONT) if bullet else "") + "</w:lvl>")
        return "".join(out_)

    numbering = (f"{HEAD}<w:numbering {W}>"
                 f'<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>{levels(True)}</w:abstractNum>'
                 f'<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>{levels(False)}</w:abstractNum>'
                 '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
                 + "".join(f'<w:num w:numId="{n}"><w:abstractNumId w:val="1"/>'
                           + "".join(f'<w:lvlOverride w:ilvl="{l}"><w:startOverride w:val="1"/></w:lvlOverride>'
                                     for l in range(3)) + "</w:num>" for n in num_defs)
                 + "</w:numbering>")
    settings = (f'{HEAD}<w:settings {W}><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/>'
                '<w:characterSpacingControl w:val="doNotCompress"/><w:updateFields w:val="true"/>'
                '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
                "</w:settings>")
    fonts = (f"{HEAD}<w:fonts {W}>" + "".join(f'<w:font w:name="{f}"><w:family w:val="{fam}"/>'
                                               f'<w:pitch w:val="{pitch}"/></w:font>'
                                               for f, fam, pitch in ((FONT, "swiss", "variable"), (MONO, "modern", "fixed")))
             + "</w:fonts>")
    header_txt = meta.title + (f"  \u00b7  {_short(meta.units)}" if meta.units else "")
    header = (f"{HEAD}<w:hdr {W}><w:p>{_ppr(borders={'bottom': (4, RULE, 4)}, jc='right')}"
              f"{_run(header_txt, size=8, color=GREY)}</w:p></w:hdr>")
    footer = (f"{HEAD}<w:ftr {W}><w:p>{_ppr(jc='center')}{_run('Page ', size=8.5, color=GREY)}"
              f"{_fld('PAGE', size=8.5, color=GREY)}{_run(' of ', size=8.5, color=GREY)}"
              f"{_fld('NUMPAGES', size=8.5, color=GREY)}</w:p></w:ftr>")
    empty_hdr = f"{HEAD}<w:hdr {W}><w:p/></w:hdr>"
    empty_ftr = f"{HEAD}<w:ftr {W}><w:p/></w:ftr>"

    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    doc_rels = (f'{HEAD}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(f'<Relationship Id="{i}" Type="{R}/{t}" Target="{f}"/>' for i, t, f in (
                    ("rIdStyles", "styles", "styles.xml"), ("rIdSettings", "settings", "settings.xml"),
                    ("rIdNumbering", "numbering", "numbering.xml"), ("rIdFonts", "fontTable", "fontTable.xml"),
                    ("rIdHeader", "header", "header1.xml"), ("rIdHeaderFirst", "header", "header2.xml"),
                    ("rIdFooter", "footer", "footer1.xml"), ("rIdFooterFirst", "footer", "footer2.xml")))
                + "</Relationships>")
    root_rels = (f'{HEAD}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 f'<Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                 f'<Relationship Id="rId3" Type="{R}/extended-properties" Target="docProps/app.xml"/>'
                 "</Relationships>")
    WML = "application/vnd.openxmlformats-officedocument.wordprocessingml"
    content_types = (f'{HEAD}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     + "".join(f'<Override PartName="/word/{n}" ContentType="{WML}.{t}+xml"/>' for n, t in (
                         ("document.xml", "document.main"), ("styles.xml", "styles"), ("settings.xml", "settings"),
                         ("numbering.xml", "numbering"), ("fontTable.xml", "fontTable"),
                         ("header1.xml", "header"), ("header2.xml", "header"),
                         ("footer1.xml", "footer"), ("footer2.xml", "footer")))
                     + '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                     '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
                     "</Types>")
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = (f'{HEAD}<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{_x(meta.title)}</dc:title><dc:subject>{_x(meta.units)}</dc:subject>"
            "<dc:creator>Reversa</dc:creator>"
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>')
    app = (f'{HEAD}<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
           "<Application>Reversa</Application></Properties>")

    tmp = Path(str(out) + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/settings.xml", settings)
        z.writestr("word/numbering.xml", numbering)
        z.writestr("word/fontTable.xml", fonts)
        z.writestr("word/header1.xml", header)
        z.writestr("word/header2.xml", empty_hdr)
        z.writestr("word/footer1.xml", footer)
        z.writestr("word/footer2.xml", empty_ftr)
    os.replace(tmp, out)


def _short(units: str, limit: int = 40) -> str:
    return units if len(units) <= limit else units[: limit - 1] + "\u2026"


# =====================================================================================
# 3. optional pagination pass (fills TOC page numbers for non-Word viewers)
# =====================================================================================
def _heading_pages(docx: Path, headings: list[dict], timeout: int) -> dict[str, int] | None:
    mac_app = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    soffice = (shutil.which("soffice") or shutil.which("libreoffice")
               or (mac_app if os.path.exists(mac_app) else None))
    pdftotext = shutil.which("pdftotext") or next(
        (p for p in ("/opt/homebrew/bin/pdftotext", "/usr/local/bin/pdftotext") if os.path.exists(p)), None)
    if not soffice or not pdftotext:
        return None
    with tempfile.TemporaryDirectory(prefix="reversa_pdf_") as tmp:
        try:
            subprocess.run([soffice, f"-env:UserInstallation=file://{tmp}/profile", "--headless",
                            "--convert-to", "pdf", "--outdir", tmp, str(docx)],
                           capture_output=True, timeout=timeout, check=True)
            pdf = Path(tmp) / (docx.stem + ".pdf")
            text = subprocess.run([pdftotext, "-layout", str(pdf), "-"], capture_output=True,
                                  text=True, timeout=timeout, check=True).stdout
        except (subprocess.SubprocessError, OSError):
            return None
    norm = lambda s: re.sub(r"[^\w]+", " ", s).strip().lower()
    page_lines = [[norm(l) for l in pg.splitlines()] for pg in text.split("\f")]
    pages, cur = {}, 1
    toc = [h for h in headings if h["level"] <= 2]
    # skip past the Contents pages: start after the page listing the last entry
    last = norm(toc[-1]["num"] + " " + toc[-1]["text"])[:40] if toc else ""
    for p, lines in enumerate(page_lines, 1):
        if any(l.startswith(last) for l in lines):
            cur = p + 1
            break
    for h in toc:
        key = norm(h["num"] + " " + h["text"])[:40]
        for p in range(cur, len(page_lines) + 1):
            if any(l.startswith(key) for l in page_lines[p - 1]):
                pages[h["id"]] = cur = p
                break
        else:
            return None                                   # never ship a partial TOC
    return pages


def build_docx(sdd: Path | str, out: Path | str, title: str = "Operational Specification",
               files: list[Path] | None = None, paginate: str | None = None) -> Path:
    """Render every Markdown artifact under `sdd` into one styled Word document.
    paginate: "auto" (default; uses LibreOffice + pdftotext when present), or "off".
    Env override: REVERSA_DOCX_PAGINATE."""
    sdd, out = Path(sdd), Path(out)
    files = files if files is not None else ordered_markdown_files(sdd)
    if not files:
        raise ValueError(f"no Markdown artifacts under {sdd}")
    ir, meta = to_ir(((f.relative_to(sdd).as_posix(), f.read_text(encoding="utf-8", errors="replace"))
                      for f in files), title)
    mode = (paginate or os.environ.get("REVERSA_DOCX_PAGINATE", "auto")).lower()
    pages = None
    if mode != "off":
        # first pass with two-digit placeholders, so the Contents takes the same space
        _render(ir, meta, out, {h["id"]: "00" for h in meta.headings})
        pages = _heading_pages(out, meta.headings, int(os.environ.get("REVERSA_DOCX_TIMEOUT", "180")))
    _render(ir, meta, out, pages)
    return out
