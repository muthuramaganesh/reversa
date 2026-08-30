"""Lightweight static analysis used by the heuristic backend.

Every extracted fact carries the line where it was found so the resulting
claim can cite evidence. COBOL gets first-class support (the paper's case
study is COBOL); other languages get a generic def/import/if/raise scan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

ERROR_WORDS = re.compile(
    r"\b(erro|error|invalid|inval|insuficiente|insufficient|limite|limit|exced|"
    r"negad|denied|fail|falh|bloque|block|nao|não|not\s+allowed|abort|excep|deve|must|"
    r"inexist|not\s+found|sem\s)", re.I)


@dataclass
class Fact:
    kind: str          # program, paragraph, section, call, perform, select, fd,
                       # record, condition, dispatch, case, message, accept,
                       # display, stop, function, class, import, raise, io
    name: str
    line: int
    detail: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class FileFacts:
    path: str
    language: str
    facts: list[Fact] = field(default_factory=list)

    def of(self, *kinds: str) -> list[Fact]:
        return [f for f in self.facts if f.kind in kinds]

    def first(self, kind: str) -> Fact | None:
        fs = self.of(kind)
        return fs[0] if fs else None


# --------------------------------------------------------------------------
# COBOL
# --------------------------------------------------------------------------
_DIV = re.compile(r"^\s*(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION\b", re.I)
_PROG = re.compile(r"PROGRAM-ID\s*\.\s*([A-Z0-9-]+)", re.I)
_SECTION = re.compile(r"^\s*([A-Z0-9-]+)\s+SECTION\s*\.", re.I)
_PARA = re.compile(r"^\s{0,7}([A-Z][A-Z0-9-]*)\s*\.\s*$", re.I)
_CALL = re.compile(r"\bCALL\s+['\"]([A-Za-z0-9-]+)['\"]", re.I)
_PERFORM = re.compile(r"\bPERFORM\s+([A-Z][A-Z0-9-]+)", re.I)
_SELECT = re.compile(r"\bSELECT\s+([A-Z0-9-]+)\s+ASSIGN\s+TO\s+['\"]?([^\s'\".]+)", re.I)
_ORG = re.compile(r"ORGANIZATION\s+(?:IS\s+)?([A-Z]+)", re.I)
_FD = re.compile(r"^\s*FD\s+([A-Z0-9-]+)", re.I)
_LVL01 = re.compile(r"^\s*01\s+([A-Z0-9-]+)", re.I)
_FIELD = re.compile(r"^\s*(\d\d)\s+([A-Z0-9-]+)(?:\s+PIC(?:TURE)?\s+(?:IS\s+)?([^\s.]+(?:\.\d+)?))?"
                    r"(?:\s+VALUE\s+(?:IS\s+)?('[^']*'|\"[^\"]*\"|[-+]?\d+(?:\.\d+)?|[A-Z-]+))?\s*\.?\s*$", re.I)
_IF = re.compile(r"^\s*IF\s+(.+?)\s*$", re.I)
_EVAL = re.compile(r"^\s*EVALUATE\s+(.+?)\s*$", re.I)
_WHEN = re.compile(r"^\s*WHEN\s+(.+?)\s*$", re.I)
_DISPLAY = re.compile(r"\bDISPLAY\s+(.+)", re.I)
_ACCEPT = re.compile(r"\bACCEPT\s+([A-Z0-9-]+)", re.I)
_STOP = re.compile(r"\b(STOP\s+RUN|GOBACK|EXIT\s+PROGRAM)\b", re.I)
_IO = re.compile(r"^\s*(READ|WRITE|REWRITE|DELETE|START)\s+([A-Z0-9-]+)", re.I)
_OPENCLOSE = re.compile(r"^\s*(OPEN|CLOSE)\s+(.+?)\s*\.?\s*$", re.I)
_OPEN_MODES = {"INPUT", "OUTPUT", "I-O", "EXTEND"}
_STR = re.compile(r"['\"]([^'\"]{3,})['\"]")
_KEYWORDS = {"IF", "ELSE", "END-IF", "EVALUATE", "END-EVALUATE", "PERFORM", "END-PERFORM",
             "MOVE", "DISPLAY", "ACCEPT", "COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE",
             "OPEN", "CLOSE", "READ", "WRITE", "REWRITE", "DELETE", "START", "STOP", "GOBACK",
             "EXIT", "CALL", "STRING", "UNSTRING", "INSPECT", "INITIALIZE", "SET", "WHEN",
             "CONTINUE", "NOT", "END-READ", "END-CALL", "END-STRING", "GO", "THEN"}


def _is_comment(line: str) -> bool:
    s = line.lstrip()
    return s.startswith("*>") or s.startswith("*") or (len(line) > 6 and line[6] in "*/")


def analyze_cobol(path: str, lines: list[str]) -> FileFacts:
    ff = FileFacts(path, "cobol")
    division = ""
    in_ws = False
    data_section = ""
    current_record = ""
    current_para = ""
    for i, raw in enumerate(lines, start=1):
        if _is_comment(raw):
            continue
        line = raw.rstrip()
        m = _DIV.match(line)
        if m:
            division = m.group(1).upper()
            in_ws = False
            continue
        m = _PROG.search(line)
        if m:
            ff.facts.append(Fact("program", m.group(1).upper(), i))
            continue
        m = _SECTION.match(line)
        if m:
            name = m.group(1).upper()
            if division == "DATA":
                data_section = name
                in_ws = name == "WORKING-STORAGE"
            if division == "PROCEDURE":
                ff.facts.append(Fact("section", name, i))
            continue
        if division == "ENVIRONMENT":
            m = _SELECT.search(line)
            if m:
                org = _ORG.search(line)
                ff.facts.append(Fact("select", m.group(1).upper(), i, m.group(2),
                                     {"organization": org.group(1).upper() if org else ""}))
            elif ff.facts and ff.facts[-1].kind == "select" and _ORG.search(line):
                ff.facts[-1].extra["organization"] = _ORG.search(line).group(1).upper()
            continue
        if division == "DATA":
            m = _FD.match(line)
            if m:
                ff.facts.append(Fact("fd", m.group(1).upper(), i))
                continue
            m = _LVL01.match(line)
            if m:
                ff.facts.append(Fact("record", m.group(1).upper(), i,
                                     data_section.lower() or "file"))
                current_record = m.group(1).upper()
            m = _FIELD.match(line)
            if m and m.group(3):
                lvl, name, pic, val = m.group(1), m.group(2).upper(), m.group(3), (m.group(4) or "").strip()
                if lvl == "01":
                    if val:
                        ff.facts.append(Fact("constant", name, i, val, {"pic": pic, "section": data_section.lower()}))
                else:
                    ff.facts.append(Fact("field", name, i, current_record,
                                         {"pic": pic, "value": val, "section": data_section.lower()}))
            continue
        if division == "PROCEDURE":
            m = _PARA.match(line)
            if m and m.group(1).upper() not in _KEYWORDS:
                current_para = m.group(1).upper()
                ff.facts.append(Fact("paragraph", current_para, i))
                continue
            for m in _CALL.finditer(line):
                ff.facts.append(Fact("call", m.group(1).upper(), i, current_para))
            for m in _PERFORM.finditer(line):
                tgt = m.group(1).upper()
                if tgt not in _KEYWORDS and tgt not in ("UNTIL", "VARYING", "WITH"):
                    ff.facts.append(Fact("perform", tgt, i, current_para))
            m = _IF.match(line)
            if m:
                ff.facts.append(Fact("condition", m.group(1).rstrip("."), i, current_para))
            m = _EVAL.match(line)
            if m:
                ff.facts.append(Fact("dispatch", m.group(1), i, current_para))
            m = _WHEN.match(line)
            if m:
                ff.facts.append(Fact("case", m.group(1), i, current_para))
            m = _DISPLAY.search(line)
            if m:
                s = _STR.search(m.group(1))
                text = s.group(1) if s else m.group(1)
                kind = "message" if ERROR_WORDS.search(text) else "display"
                ff.facts.append(Fact(kind, text.strip(), i, current_para))
            m = _ACCEPT.search(line)
            if m:
                ff.facts.append(Fact("accept", m.group(1).upper(), i, current_para))
            m = _IO.match(line)
            if m:
                ff.facts.append(Fact("io", m.group(2).upper(), i, m.group(1).upper(),
                                     {"paragraph": current_para}))
            m = _OPENCLOSE.match(line)
            if m:
                verb = m.group(1).upper()
                mode = ""
                for tok in m.group(2).upper().replace(".", " ").split():
                    if tok in _OPEN_MODES:
                        mode = tok
                    elif tok not in _KEYWORDS:
                        ff.facts.append(Fact("io", tok, i, f"{verb} {mode}".strip(),
                                             {"paragraph": current_para}))
            if _STOP.search(line):
                ff.facts.append(Fact("stop", _STOP.search(line).group(1).upper(), i, current_para))
    return ff


# --------------------------------------------------------------------------
# Generic (python / js / java / go / ...)
# --------------------------------------------------------------------------
_G_DEF = re.compile(r"^\s*(?:async\s+)?(?:def|function|func|fn|sub|procedure)\s+([A-Za-z_][\w]*)", re.I)
_G_METHOD = re.compile(r"^\s*(?:public|private|protected|static|\s)*[\w<>\[\]]+\s+([A-Za-z_]\w*)\s*\([^;]*\)\s*\{")
_G_CLASS = re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?(?:class|struct|interface|type)\s+([A-Za-z_]\w*)")
_G_IMPORT = re.compile(r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import|require\(['\"]([^'\"]+)['\"]\)|#include\s+[<\"]([^>\"]+)[>\"])")
_G_IF = re.compile(r"^\s*(?:else\s+)?if\s*\(?(.+?)\)?\s*[:{]?\s*$")
_G_RAISE = re.compile(r"^\s*(?:raise|throw)\s+(.+)")
_G_IO = re.compile(r"\b(open\(|sqlite3|psycopg|mysql|pymongo|fopen|readFile|writeFile|SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET)", re.I)
_G_MAIN = re.compile(r"(if\s+__name__\s*==\s*['\"]__main__['\"]|func\s+main\s*\(|public\s+static\s+void\s+main|^\s*main\s*\()")
_G_MSG = re.compile(r"['\"]([^'\"]{4,})['\"]")


def analyze_generic(path: str, language: str, lines: list[str]) -> FileFacts:
    ff = FileFacts(path, language)
    current = ""
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        s = line.strip()
        if not s or (s.startswith("#") and not s.startswith("#include")) or s.startswith(("//", "/*", "*")):
            continue
        m = _G_CLASS.match(line)
        if m:
            ff.facts.append(Fact("class", m.group(1), i))
            continue
        m = _G_DEF.match(line) or (_G_METHOD.match(line) if language in ("java", "csharp", "cpp", "c") else None)
        if m and m.group(1) not in ("if", "for", "while", "switch", "return"):
            current = m.group(1)
            ff.facts.append(Fact("function", current, i))
            continue
        m = _G_IMPORT.match(line)
        if m:
            ff.facts.append(Fact("import", next(g for g in m.groups() if g), i))
            continue
        if _G_MAIN.search(line):
            ff.facts.append(Fact("stop", "entry-point", i, current))
        m = _G_IF.match(line)
        if m:
            ff.facts.append(Fact("condition", m.group(1), i, current))
        m = _G_RAISE.match(line)
        if m:
            msg = _G_MSG.search(m.group(1))
            ff.facts.append(Fact("message", (msg.group(1) if msg else m.group(1))[:80], i, current))
        m = _G_IO.search(line)
        if m:
            ff.facts.append(Fact("io", m.group(1).split("(")[0].strip(), i, current))
    return ff


def analyze(path: str, language: str, lines: list[str]) -> FileFacts:
    if language.startswith("cobol"):
        return analyze_cobol(path, lines)
    return analyze_generic(path, language, lines)


def pic_english(pic: str) -> str:
    """Describe a COBOL PICTURE clause in plain English."""
    p = pic.upper()
    signed = p.startswith("S")
    p = p.lstrip("S")
    def count(sym: str) -> int:
        n = 0
        for m in re.finditer(re.escape(sym) + r"(?:\((\d+)\))?", p):
            n += int(m.group(1)) if m.group(1) else 1
        return n
    if "V" in p:
        ip, dp = p.split("V", 1)
        return (f"{'signed ' if signed else ''}amount with {_cnt(dp, '9')} decimal place(s), "
                f"up to {_cnt(ip, '9')} digit(s) before the point")
    if set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"):
        return f"{count('9')}-digit number"
    if "X" in p:
        return f"{count('X')}-character text"
    if "Z" in p or "-" in p or "," in p:
        return "formatted display of a number"
    return f"picture {pic}"


def _cnt(seg: str, sym: str) -> int:
    n = 0
    for m in re.finditer(re.escape(sym) + r"(?:\((\d+)\))?", seg):
        n += int(m.group(1)) if m.group(1) else 1
    return n


_IF_OPEN = re.compile(r"^\s*IF\b", re.I)
_IF_CLOSE = re.compile(r"^\s*END-IF\b", re.I)
_EXIT = re.compile(r"\b(GOBACK|STOP\s+RUN|EXIT\s+PROGRAM)\b", re.I)


def aborts_in_branch(lines: list[str], cond_line: int) -> bool:
    """True if the IF at `cond_line` contains GOBACK/STOP RUN before its END-IF (or ELSE)."""
    depth = 0
    for ln in range(cond_line, min(len(lines), cond_line + 60)):
        txt = lines[ln] if ln < len(lines) else ""
        if _IF_OPEN.match(txt):
            depth += 1
        if depth == 1 and re.match(r"^\s*ELSE\b", txt, re.I):
            return False
        if _EXIT.search(txt) and depth >= 1:
            return True
        if _IF_CLOSE.match(txt):
            depth -= 1
            if depth <= 0:
                return False
        # sentence-terminating period ends an IF without END-IF
        if depth >= 1 and txt.rstrip().endswith(".") and not _IF_OPEN.match(txt):
            return False
    return False


def excerpt(lines: list[str], line: int, n: int = 1) -> str:
    seg = lines[max(0, line - 1):max(0, line - 1) + n]
    return " ".join(s.strip() for s in seg)[:160]
