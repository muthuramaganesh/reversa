"""specbuilder: deterministic, backend-independent COBOL specification builder.

Parses the PROCEDURE DIVISION into a real block tree (IF/ELSE/END-IF,
EVALUATE/WHEN/END-EVALUATE, sentence-ending periods) and derives from it:

  * business rules in plain English, each with a worked example, a confidence
    level and a code reference (the rule text is written for business
    analysts; the code text is kept as technical detail, never deleted);
  * decision tables, classified as LOOKUP TABLE or STATE MACHINE;
  * automated cross-checks (gaps and contradictions);
  * a coverage report proving every executable statement is explained;
  * a layered operational specification that goes from generic to specific.

Confidence discipline (unchanged from the rest of Reversa):
  confirmed - read literally from the code (condition + the actions it guards)
  inferred  - business meaning we deduce but the code does not state
              (e.g. an error message "rejects" the payment)
  gap       - could not be determined from the code; needs a human
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .analysis import field_english, value_english, condition_english, ERROR_WORDS

# --------------------------------------------------------------------------
# Lexing
# --------------------------------------------------------------------------
_PARA = re.compile(r"^\s*([A-Z0-9][A-Z0-9-]*)(\s+SECTION)?\s*\.\s*$", re.I)
_KEYWORD_PARAS = {"END-IF", "END-EVALUATE", "ELSE", "CONTINUE", "GOBACK", "EXIT",
                  "END-PERFORM", "END-READ", "END-COMPUTE"}
_IF = re.compile(r"^\s*IF\s+(.+?)\s*\.?\s*$", re.I)
_ELSE = re.compile(r"^\s*ELSE\b", re.I)
_END_IF = re.compile(r"^\s*END-IF\b", re.I)
_EVAL = re.compile(r"^\s*EVALUATE\s+(.+?)\s*$", re.I)
_WHEN = re.compile(r"^\s*WHEN\s+(.+?)\s*\.?\s*$", re.I)
_END_EVAL = re.compile(r"^\s*END-EVALUATE\b", re.I)
_MOVE = re.compile(r"^\s*MOVE\s+(.+?)\s+TO\s+([A-Z0-9][A-Z0-9-]*)\s*\.?\s*$", re.I)
_COMPUTE = re.compile(r"^\s*COMPUTE\s+([A-Z0-9][A-Z0-9-]*)(?:\s+ROUNDED)?\s*=\s*(.+?)\s*\.?\s*$", re.I)
_ARITH = re.compile(r"^\s*(ADD|SUBTRACT|MULTIPLY|DIVIDE)\s+(.+?)\s*\.?\s*$", re.I)
_PERFORM = re.compile(r"^\s*PERFORM\s+([A-Z0-9][A-Z0-9-]*)(.*?)\s*\.?\s*$", re.I)
_GOTO = re.compile(r"^\s*GO\s+TO\s+([A-Z0-9][A-Z0-9-]*)\s*\.?\s*$", re.I)
_DISPLAY = re.compile(r"^\s*DISPLAY\s+(.+?)\s*\.?\s*$", re.I)
_CALL = re.compile(r"^\s*CALL\s+['\"]?([A-Z0-9-]+)['\"]?(.*?)\s*\.?\s*$", re.I)
_STOP = re.compile(r"^\s*(STOP\s+RUN|GOBACK|EXIT\s+PROGRAM)\b", re.I)
_CONTINUE = re.compile(r"^\s*CONTINUE\s*\.?\s*$", re.I)
_EXIT = re.compile(r"^\s*EXIT\s*\.?\s*$", re.I)
_STR = re.compile(r"'([^']*)'|\"([^\"]*)\"")
_DATA_ITEM = re.compile(r"^\s*(\d\d)\s+([A-Z0-9][A-Z0-9-]*)(.*)$", re.I)
_LEVEL88 = re.compile(r"^\s*88\s+([A-Z0-9][A-Z0-9-]*)\s+VALUES?\s+(?:IS\s+|ARE\s+)?(.+?)\s*\.?\s*$", re.I)
_CMP1 = re.compile(r"^\s*([A-Z0-9][A-Z0-9-]*)\s*(NOT\s*=|>=|<=|=|>|<)\s*(.+?)\s*$", re.I)
_TERMINATES = ("stop", "goto")


@dataclass
class Stmt:
    kind: str            # move|compute|arith|perform|goto|display|call|stop|continue|exit|other
    line: int
    text: str
    target: str = ""     # field written, or paragraph jumped to
    value: str = ""      # value/expression/message
    reads: list[str] = field(default_factory=list)


@dataclass
class Block:
    kind: str                      # para|if|eval
    line: int
    text: str                      # condition / subject / paragraph name
    para: str = ""
    then: list = field(default_factory=list)
    other: list = field(default_factory=list)   # ELSE body
    cases: list = field(default_factory=list)   # [(when_text, line, [items])]
    end_line: int = 0


_INLINE_VERB = re.compile(r"\s+(?:THEN\s+)?((?:MOVE|COMPUTE|ADD|SUBTRACT|MULTIPLY|DIVIDE|PERFORM|DISPLAY|"
                          r"GO\s+TO|CONTINUE|CALL|SET|STOP\s+RUN|GOBACK|INITIALIZE|STRING|WRITE|READ)\b.*)$", re.I)


def _split_inline(text: str) -> tuple[str, str | None]:
    """'CH-CARD MOVE 0.0290 TO X' -> ('CH-CARD', 'MOVE 0.0290 TO X')."""
    m = _INLINE_VERB.search(text)
    if not m or not text[:m.start()].strip():
        return text.strip(), None
    return text[:m.start()].strip(), m.group(1).strip()


def _clean(line: str) -> str:
    # free-format and fixed-format tolerant: drop sequence area & comment lines
    if len(line) > 6 and line[:6].strip().isdigit():
        line = line[6:]
    s = line.rstrip()
    if s.lstrip().startswith("*") or s.lstrip().startswith("*>"):
        return ""
    return s


def _fields_in(expr: str) -> list[str]:
    out = []
    for tok in re.findall(r"[A-Z][A-Z0-9-]*[A-Z0-9]|[A-Z]", re.sub(r"'[^']*'|\"[^\"]*\"", " ", expr.upper())):
        if tok in {"AND", "OR", "NOT", "ZERO", "ZEROS", "ZEROES", "SPACE", "SPACES", "TRUE",
                   "FALSE", "TO", "BY", "FROM", "GIVING", "INTO", "ROUNDED", "OTHER", "THRU",
                   "THROUGH", "UNTIL", "TIMES", "VARYING", "HIGH-VALUES", "LOW-VALUES", "IS",
                   "GREATER", "LESS", "EQUAL", "THAN", "NUMERIC", "ALPHABETIC", "UPON", "CONSOLE"}:
            continue
        out.append(tok)
    return out


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------
@dataclass
class Program:
    name: str
    path: str
    lines: list[str]
    paras: list[Block]
    data: dict[str, dict]                 # field -> {level, section, value, line}
    flags: dict[str, tuple[str, str]]     # 88 name -> (parent field, value)
    exec_lines: set[int]                  # executable statement lines (for coverage)


def parse(path: str, lines: list[str]) -> Program:
    clean = [_clean(l) for l in lines]
    name = path.rsplit("/", 1)[-1].rsplit(".", 1)[0].upper()
    for s in clean:
        m = re.match(r"^\s*PROGRAM-ID\.\s*([A-Z0-9-]+)", s, re.I)
        if m:
            name = m.group(1).upper()
            break

    # ---- data division --------------------------------------------------
    data: dict[str, dict] = {}
    flags: dict[str, tuple[str, str]] = {}
    section = ""
    parent = ""
    proc_start = len(clean)
    for i, s in enumerate(clean):
        if re.match(r"^\s*PROCEDURE\s+DIVISION", s, re.I):
            proc_start = i
            break
        m = re.match(r"^\s*(WORKING-STORAGE|LINKAGE|FILE|LOCAL-STORAGE)\s+SECTION", s, re.I)
        if m:
            section = m.group(1).upper()
            continue
        m = _LEVEL88.match(s)
        if m and parent:
            flags[m.group(1).upper()] = (parent, m.group(2).strip())
            continue
        m = _DATA_ITEM.match(s)
        if m and m.group(1) != "88":
            fname = m.group(2).upper()
            if fname == "FILLER":
                continue
            vm = re.search(r"\bVALUE\s+(?:IS\s+)?(.+?)\s*\.?\s*$", m.group(3), re.I)
            data[fname] = {"level": m.group(1), "section": section,
                           "value": vm.group(1) if vm else None, "line": i + 1,
                           "pic": (re.search(r"PIC(?:TURE)?\s+(\S+)", m.group(3), re.I) or [None, ""])[1]}
            parent = fname

    # ---- procedure division --------------------------------------------
    paras: list[Block] = []
    exec_lines: set[int] = set()
    cur = Block("para", proc_start + 1, "(MAIN)", para="(MAIN)")
    paras.append(cur)
    stack: list[tuple[Block, str]] = []   # (block, which list: then|other|case)

    def sink() -> list:
        if not stack:
            return cur.then
        blk, where = stack[-1]
        if where == "then":
            return blk.then
        if where == "other":
            return blk.other
        return blk.cases[-1][2]

    def close_all(at: int) -> None:
        while stack:
            stack.pop()[0].end_line = at

    i = proc_start + 1
    while i < len(clean):
        s = clean[i]
        ln = i + 1
        i += 1
        if not s.strip():
            continue
        ends_sentence = s.rstrip().endswith(".")
        pm = _PARA.match(s)
        if pm and pm.group(1).upper() not in _KEYWORD_PARAS and not stack:
            cur = Block("para", ln, pm.group(1).upper(), para=pm.group(1).upper())
            paras.append(cur)
            continue
        m = _IF.match(s)
        if m:
            cond = m.group(1)
            # continuation lines (AND/OR on the next line)
            while i < len(clean) and re.match(r"^\s*(AND|OR)\b", clean[i], re.I):
                cond += " " + clean[i].strip().rstrip(".")
                i += 1
            cond, inline = _split_inline(cond.strip().rstrip("."))
            cond = re.sub(r"\s+THEN\s*$", "", cond, flags=re.I)
            blk = Block("if", ln, cond, para=cur.para)
            sink().append(blk)
            exec_lines.add(ln)
            stack.append((blk, "then"))
            if inline:
                st = _stmt(inline, ln)
                if st:
                    blk.then.append(st)
            if ends_sentence:
                close_all(ln)
            continue
        if _ELSE.match(s):
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0].kind == "if":
                    stack[k] = (stack[k][0], "other")
                    del stack[k + 1:]
                    rest = re.sub(r"^\s*ELSE\b", "", s, flags=re.I).strip()
                    if rest:
                        st = _stmt(rest, ln)
                        if st:
                            stack[k][0].other.append(st)
                    break
            if ends_sentence:
                close_all(ln)
            continue
        if _END_IF.match(s):
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0].kind == "if":
                    stack[k][0].end_line = ln
                    del stack[k:]
                    break
            if ends_sentence:
                close_all(ln)
            continue
        m = _EVAL.match(s)
        if m:
            blk = Block("eval", ln, m.group(1).strip().rstrip("."), para=cur.para)
            sink().append(blk)
            exec_lines.add(ln)
            stack.append((blk, "case"))
            continue
        m = _WHEN.match(s)
        if m and stack:
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0].kind == "eval":
                    val, inline = _split_inline(m.group(1).strip().rstrip("."))
                    body = []
                    if inline:
                        st = _stmt(inline, ln)
                        if st:
                            body.append(st)
                    stack[k][0].cases.append((val, ln, body))
                    stack[k] = (stack[k][0], "case")
                    del stack[k + 1:]
                    break
            exec_lines.add(ln)
            continue
        if _END_EVAL.match(s):
            for k in range(len(stack) - 1, -1, -1):
                if stack[k][0].kind == "eval":
                    stack[k][0].end_line = ln
                    del stack[k:]
                    break
            if ends_sentence:
                close_all(ln)
            continue
        st = _stmt(s, ln)
        if st:
            if st.kind != "eval_orphan":
                target = sink() if (stack and (stack[-1][1] != "case" or stack[-1][0].cases)) else cur.then
                target.append(st)
                exec_lines.add(ln)
        if ends_sentence:
            close_all(ln)
    return Program(name, path, lines, paras, data, flags, exec_lines)


def _stmt(s: str, ln: int) -> Stmt | None:
    m = _MOVE.match(s)
    if m:
        return Stmt("move", ln, s.strip(), target=m.group(2).upper(), value=m.group(1).strip(),
                    reads=_fields_in(m.group(1)))
    m = _COMPUTE.match(s)
    if m:
        return Stmt("compute", ln, s.strip(), target=m.group(1).upper(), value=m.group(2).strip(),
                    reads=_fields_in(m.group(2)))
    m = _ARITH.match(s)
    if m:
        body = m.group(2)
        tgt = ""
        g = re.search(r"\bGIVING\s+([A-Z0-9-]+)", body, re.I) or re.search(r"\b(?:TO|FROM|INTO|BY)\s+([A-Z0-9-]+)\s*$", body, re.I)
        if g:
            tgt = g.group(1).upper()
        return Stmt("arith", ln, s.strip(), target=tgt, value=f"{m.group(1).upper()} {body}",
                    reads=_fields_in(body))
    m = _PERFORM.match(s)
    if m:
        return Stmt("perform", ln, s.strip(), target=m.group(1).upper(), value=m.group(2).strip())
    m = _GOTO.match(s)
    if m:
        return Stmt("goto", ln, s.strip(), target=m.group(1).upper())
    m = _DISPLAY.match(s)
    if m:
        sm = _STR.search(m.group(1))
        return Stmt("display", ln, s.strip(), value=(sm.group(1) or sm.group(2)) if sm else m.group(1),
                    reads=[] if sm else _fields_in(m.group(1)))
    m = _CALL.match(s)
    if m:
        return Stmt("call", ln, s.strip(), target=m.group(1).upper(), reads=_fields_in(m.group(2)))
    if _STOP.match(s):
        return Stmt("stop", ln, s.strip())
    if _CONTINUE.match(s):
        return Stmt("continue", ln, s.strip())
    if _EXIT.match(s):
        return Stmt("exit", ln, s.strip())
    if re.match(r"^\s*(DATA|IDENTIFICATION|ENVIRONMENT|PROCEDURE)\s+DIVISION", s, re.I):
        return None
    return Stmt("other", ln, s.strip(), reads=_fields_in(s))


# --------------------------------------------------------------------------
# Plain-English rendering
# --------------------------------------------------------------------------
def _num(v: str) -> float | None:
    try:
        return float(v.replace(",", ""))
    except ValueError:
        return None


def _money(x: float) -> str:
    return f"{x:,.2f}"


def _pct_phrase(v: str) -> str:
    n = _num(v)
    if n is not None and 0 < n < 1:
        return f"{v} ({n * 100:.2f}%)"
    return value_english(v)


def expr_english(expr: str) -> str:
    t = expr
    for f in sorted(set(_fields_in(expr)), key=len, reverse=True):
        t = re.sub(rf"(?<![A-Z0-9-]){re.escape(f)}(?![A-Z0-9-])", f"[{field_english(f)}]", t, flags=re.I)
    t = t.replace("*", " × ").replace("/", " ÷ ").replace("**", "^")
    return re.sub(r"\s+", " ", t).strip()


def action_english(st: Stmt, prog: Program) -> str:
    if st.kind == "move":
        fe = field_english(st.target)
        if "pct" in st.target.lower() or "percent" in st.target.lower():
            return f"set the {fe} to {_pct_phrase(st.value)}"
        src = st.value
        if re.match(r"^[A-Z][A-Z0-9-]*$", src, re.I) and src.upper() not in {"ZERO", "ZEROS", "SPACES", "SPACE"}:
            return f"copy the {field_english(src)} into the {fe}"
        return f"set the {fe} to {value_english(src)}"
    if st.kind == "compute":
        return f"calculate the {field_english(st.target)} as {expr_english(st.value)}"
    if st.kind == "arith":
        verb, _, rest = st.value.partition(" ")
        def fe(x):
            x = x.strip()
            return f"the {field_english(x)}" if re.match(r"^[A-Z][A-Z0-9-]*$", x, re.I) else x
        m = re.match(r"^(.+?)\s+(TO|FROM|BY|INTO)\s+([A-Z0-9-]+)(?:\s+GIVING\s+([A-Z0-9-]+))?", rest, re.I)
        if m:
            a, prep, b, giving = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
            core = {"ADD": f"add {fe(a)} to {fe(b)}", "SUBTRACT": f"subtract {fe(a)} from {fe(b)}",
                    "MULTIPLY": f"multiply {fe(b)} by {fe(a)}", "DIVIDE": f"divide {fe(b)} by {fe(a)}"}.get(verb.upper(),
                    st.value.lower())
            return core + (f", storing the result in {fe(giving)}" if giving else "")
        return f"update the {field_english(st.target) if st.target else 'value'} ({st.value.lower()})"
    if st.kind == "perform":
        return f"run the step \"{_para_english(st.target)}\""
    if st.kind == "goto":
        return f"jump to the step \"{_para_english(st.target)}\""
    if st.kind == "display":
        return f"show the message \"{st.value}\""
    if st.kind == "call":
        return f"call the external program {st.target}"
    if st.kind == "stop":
        return "end the program"
    if st.kind == "continue":
        return "take no action"
    if st.kind == "exit":
        return "leave the current step"
    return f"perform: {st.text}"


def _para_english(p: str) -> str:
    return " ".join(w.lower() for w in p.split("-")).capitalize()


def _flag_group(names: list[str]) -> tuple[str, list[str]] | None:
    parts = [n.upper().split("-") for n in names]
    if len(parts) > 1 and all(len(p) > 1 for p in parts) and len({p[0] for p in parts}) == 1:
        return field_english(parts[0][0]), [field_english("-".join(p[1:])) for p in parts]
    return None


def _or_list(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " or " + xs[-1]


def _cond_english(cond: str, prog: Program) -> str:
    c = cond.strip()
    m = re.match(r"^(NOT\s*\()?\s*([A-Z0-9-]+(?:\s+OR\s+[A-Z0-9-]+)+)\s*\)?\s*$", c, re.I)
    if m:
        names = re.split(r"\s+OR\s+", m.group(2).strip(), flags=re.I)
        g = _flag_group(names)
        if g:
            what, opts = g
            if m.group(1):
                return f"no {what} ({_or_list(opts)}) is selected"
            return f"the {what} is {_or_list(opts)}"
    # 88-level condition names -> "<parent> is <value>"
    for flag, (parent, val) in prog.flags.items():
        c = re.sub(rf"(?<![A-Z0-9-]){flag}(?![A-Z0-9-])", f"{parent} = {val}", c, flags=re.I)
    clauses = re.split(r"\s+AND\s+", c, flags=re.I)
    ms = [_CMP1.match(x) for x in clauses]
    if len(clauses) > 1 and all(ms) and len({m.group(1).upper() for m in ms}) == 1 \
            and all(" ".join(m.group(2).upper().split()) == "NOT =" for m in ms):
        vals = [value_english(m.group(3)) for m in ms]
        head = f"the {field_english(ms[0].group(1))} is neither "
        return head + (" nor ".join(vals) if len(vals) == 2 else ", ".join(vals[:-1]) + " nor " + vals[-1])
    mm = re.match(r"^\s*FUNCTION\s+MOD\s*\(\s*([A-Z0-9-]+)\s*,\s*(\d+)\s*\)\s*(NOT\s*=|=)\s*0\s*$", c, re.I)
    if mm:
        neg = "NOT" in mm.group(3).upper()
        return f"the {field_english(mm.group(1))} is {'not ' if neg else ''}a multiple of {mm.group(2)}"
    out = condition_english(c)
    for f in sorted(prog.data, key=len, reverse=True):
        out = re.sub(rf"(?<![A-Za-z0-9-]){re.escape(f)}(?![A-Za-z0-9-])", f"the {field_english(f)}", out)
    return re.sub(r"(?<![\w.,])(\d{4,})(\.\d+)?(?![\w.])",
                  lambda m: f"{int(m.group(1)):,}{m.group(2) or ''}", out)


def _actions_english(items: list, prog: Program) -> str:
    parts = []
    for it in items:
        if isinstance(it, Stmt):
            parts.append(action_english(it, prog))
        elif isinstance(it, Block) and it.kind == "if":
            parts.append(f"apply the further check \"if {_cond_english(it.text, prog)}\"")
        elif isinstance(it, Block) and it.kind == "eval":
            parts.append("apply a further decision table")
    if not parts:
        return ""
    return parts[0] if len(parts) == 1 else ", then ".join(parts)


def _norm_op(op: str) -> str:
    op = " ".join(op.upper().split())
    return {"NOT =": "!=", "==": "="}.get(op, op)


def _val(v: str):
    v = v.strip()
    if v.upper() in {"ZERO", "ZEROS", "ZEROES"}:
        return 0.0
    n = _num(v)
    if n is not None:
        return n
    return v.strip("'\"")


def _flag_fields(names: list[str], prog: "Program") -> tuple[list[str], list[str]]:
    """For 88-level flags or prefixed switches (CH-CARD, CH-BANK): the fields they belong to
    and the option names (CARD, BANK)."""
    fields, opts = set(), []
    for n in names:
        n = n.upper()
        if n in prog.flags:
            fields.add(prog.flags[n][0])
        parts = n.split("-")
        if len(parts) > 1:
            fields.add(parts[0])
            opts.append("-".join(parts[1:]))
        else:
            opts.append(n)
    return sorted(fields), opts


def cond_facts(text: str, prog: "Program") -> list[dict]:
    """Condition text -> list of {field, fields, op, value} clauses (best effort, never raises)."""
    t = text.strip().rstrip(".")
    m = re.match(r"^(NOT\s*\()?\s*([A-Z0-9-]+(?:\s+OR\s+[A-Z0-9-]+)+)\s*\)?\s*$", t, re.I)
    if m:
        names = re.split(r"\s+OR\s+", m.group(2).strip(), flags=re.I)
        fields, opts = _flag_fields(names, prog)
        return [{"field": fields[0] if fields else "", "fields": fields,
                 "op": "none_of" if m.group(1) else "one_of", "value": opts}]
    clauses = re.split(r"\s+AND\s+", t, flags=re.I)
    ms = [_CMP1.match(c) for c in clauses]
    if len(clauses) > 1 and all(ms) and len({x.group(1).upper() for x in ms}) == 1 \
            and all(_norm_op(x.group(2)) == "!=" for x in ms):
        f = ms[0].group(1).upper()
        return [{"field": f, "fields": [f], "op": "not_in", "value": [_val(x.group(3)) for x in ms]}]
    out = []
    for c in re.split(r"\s+(?:AND|OR)\s+", t, flags=re.I):
        x = _CMP1.match(c.strip())
        if x:
            f = x.group(1).upper()
            flds = [f] + ([prog.flags[f][0]] if f in prog.flags else [])
            out.append({"field": f, "fields": flds, "op": _norm_op(x.group(2)), "value": _val(x.group(3))})
        elif re.match(r"^[A-Z0-9-]+$", c.strip(), re.I):
            fields, opts = _flag_fields([c.strip()], prog)
            out.append({"field": fields[0] if fields else c.strip().upper(), "fields": fields,
                        "op": "is", "value": opts[0] if opts else c.strip().upper()})
    return out


def act_facts(items: list) -> list[dict]:
    out = []
    for it in items:
        if not isinstance(it, Stmt):
            continue
        if it.kind == "move":
            out.append({"type": "set", "target": it.target, "value": _val(it.value)})
        elif it.kind == "compute":
            consts = [float(c) for c in re.findall(r"(?<![A-Z0-9-])(\d+(?:\.\d+)?)(?![A-Z0-9-])", it.value)]
            out.append({"type": "calculate", "target": it.target, "expr": it.value,
                        "uses": it.reads, "constants": consts})
        elif it.kind == "arith":
            out.append({"type": "update", "target": it.target, "expr": it.value})
        elif it.kind == "display":
            out.append({"type": "message", "value": it.value})
        elif it.kind in ("perform", "goto", "call"):
            out.append({"type": it.kind, "target": it.target})
        elif it.kind == "stop":
            out.append({"type": "stop"})
    return out


def _terminates(items: list) -> bool:
    return any(isinstance(it, Stmt) and it.kind in _TERMINATES for it in items)


# --------------------------------------------------------------------------
# Worked examples (always labelled illustrative; logic itself is from code)
# --------------------------------------------------------------------------
def _sample_for(cond: str) -> tuple[str, str] | None:
    """Return (field, sample value) that satisfies a simple condition."""
    parts = re.split(r"\s+(?:AND|OR)\s+", cond.strip(), flags=re.I)
    m = _CMP1.match(parts[0].strip())
    if not m:
        return None
    f, op, v = m.group(1).upper(), " ".join(m.group(2).upper().split()), m.group(3).strip()
    n = _num(v)
    if v.upper() in {"ZERO", "ZEROS", "ZEROES"}:
        n = 0.0
    if op == "=":
        return f, (value_english(v))
    if op == "NOT =":
        excluded = {x.strip("'\"").upper() for x in re.findall(r"'[^']*'|\"[^\"]*\"", cond)}
        if "CCY" in f or "CURRENCY" in f:
            cand = next(c for c in ["EUR", "GBP", "JPY", "THB", "HKD"] if c not in excluded)
            return f, f'"{cand}"'
        return f, "a value other than " + ", ".join(sorted(excluded)) if excluded else "a different value"
    if n is None:
        return None
    if op == ">":
        return f, _money(n + (0.01 if "." in v else 1))
    if op == ">=":
        return f, _money(n)
    if op == "<":
        return f, _money(max(n / 2, 0.01) if n > 0 else n - 1)
    if op == "<=":
        return f, _money(n)
    return None


def example_for_if(blk: Block, prog: Program) -> str:
    s = _sample_for(blk.text)
    then = _actions_english(blk.then, prog)
    if s:
        f, val = s
        head = f"If the {field_english(f)} is {val}"
    elif re.match(r"^\s*NOT\s*\(", blk.text, re.I):
        head = "If none of those options is selected"
    else:
        head = "When the condition holds"
    if then:
        return f"{head}, the program will {then}."
    return f"{head}, the code shows no resulting action."


def example_for_table(rows: list[tuple[str, str, str]], subject: str = "") -> str:
    """rows: (label, target_field, value)."""
    rows = sorted(rows, key=lambda r: (_num(r[2]) in (None, 1.0)))
    for label, tgt, val in rows:
        n = _num(val)
        if n is None:
            continue
        t = tgt.upper()
        if "PCT" in t or "PERCENT" in t:
            by = f"where the {subject} is {label}" if subject else f"with {label}"
            return (f"A payment of 1,000.00 {by} gets a {field_english(tgt)} of {val}, "
                    f"i.e. a fee of {_money(1000 * n)}.")
        if "RATE" in t:
            return (f"An amount of 100.00 in {label} converts at {val}, giving "
                    f"{_money(100 * n)} in the base currency.")
        return f"When the value is {label}, the {field_english(tgt)} becomes {val}."
    return ""


# --------------------------------------------------------------------------
# Spec model
# --------------------------------------------------------------------------
@dataclass
class Rule:
    id: str
    category: str          # Validation | Calculation | Decision | Processing step
    plain: str
    example: str
    confidence: str        # confirmed | inferred | gap
    lines: tuple[int, int]
    technical: str
    note: str = ""
    facts: dict = field(default_factory=dict)   # machine-readable form, for standards comparison


@dataclass
class Table:
    id: str
    subject: str
    kind: str              # Lookup table | State machine
    rows: list[tuple[str, str, int]]   # (when label, outcome english, line)
    default: str
    lines: tuple[int, int]
    technical: str
    example: str = ""
    facts: dict = field(default_factory=dict)


@dataclass
class Finding:
    id: str
    kind: str              # Contradiction | Unreachable code | Missing outcome | ...
    severity: str          # high | medium | low
    text: str
    lines: list[int]
    question: str


@dataclass
class Spec:
    program: Program
    rules: list[Rule] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    flow: list[tuple[str, str, int]] = field(default_factory=list)   # (step no, text, line)
    findings: list[Finding] = field(default_factory=list)
    intents: list = field(default_factory=list)          # (if-block, display stmt)
    covered: set[int] = field(default_factory=set)
    reads: dict[str, list[int]] = field(default_factory=dict)
    writes: dict[str, list[int]] = field(default_factory=dict)


def _walk(items: list, fn, depth=0, ctx=None):
    ctx = ctx or []
    for it in items:
        fn(it, depth, ctx)
        if isinstance(it, Block):
            if it.kind == "if":
                _walk(it.then, fn, depth + 1, ctx + [("if", it)])
                _walk(it.other, fn, depth + 1, ctx + [("else", it)])
            elif it.kind == "eval":
                for w, ln, body in it.cases:
                    _walk(body, fn, depth + 1, ctx + [("when", it, w)])


def _block_lines(blk: Block) -> set[int]:
    out = {blk.line}
    def add(it, d, c):
        out.add(it.line)
        if isinstance(it, Block) and it.kind == "eval":
            out.update(ln for _, ln, _ in it.cases)
    _walk(blk.then + blk.other + [b for c in blk.cases for b in c[2]], add)
    if blk.kind == "eval":
        out.update(ln for _, ln, _ in blk.cases)
    return out


def build(path: str, lines: list[str]) -> Spec:
    prog = parse(path, lines)
    spec = Spec(prog)
    counters = {"BR": 0, "DT": 0}

    def nid(p):
        counters[p] += 1
        return f"{p}-{counters[p]:02d}"

    # data flow (who reads / writes what)
    def df(it, d, c):
        if isinstance(it, Stmt):
            if it.target and it.kind in ("move", "compute", "arith"):
                spec.writes.setdefault(it.target, []).append(it.line)
            for r in it.reads:
                spec.reads.setdefault(r, []).append(it.line)
        elif isinstance(it, Block):
            src = it.text if it.kind == "if" else it.text
            for r in _fields_in(src):
                spec.reads.setdefault(r, []).append(it.line)
            if it.kind == "eval":
                for w, ln, _ in it.cases:
                    for r in _fields_in(w):
                        spec.reads.setdefault(r, []).append(ln)
    for p in prog.paras:
        _walk(p.then, df)

    # rules, tables and the processing flow
    step = [0]

    def ctx_prefix(ctx) -> str:
        bits = []
        for c in ctx:
            if c[0] == "if":
                bits.append(f"{_cond_english(c[1].text, prog)}")
            elif c[0] == "else":
                bits.append(f"it is NOT the case that {_cond_english(c[1].text, prog)}")
            elif c[0] == "when":
                bits.append(f"the {_subject_english(c[1].text)} is {_when_label(c[2], c[1], prog)}")
        return " and ".join(bits)

    def visit(it, depth, ctx):
        pre = ctx_prefix(ctx)
        if isinstance(it, Block) and it.kind == "if":
            then = _actions_english(it.then, prog)
            other = _actions_english(it.other, prog)
            cond = _cond_english(it.text, prog)
            full = f"{pre} and {cond}" if pre else cond
            has_msg = [s for s in it.then if isinstance(s, Stmt) and s.kind == "display"]
            err = bool(has_msg)
            conf, note = "confirmed", ""
            if not then and not other:
                plain = f"The program checks whether {full}, but no resulting action is coded."
                conf = "gap"
                note = "Condition confirmed; outcome could not be determined from the code."
            elif then and all(isinstance(s, Stmt) and s.kind == "continue" for s in it.then) and not other:
                plain = f"If {full}, the program takes no action (the check has no effect)."
                note = "Only CONTINUE is coded in this branch."
            else:
                plain = f"If {full}, the program will {then}." if then else f"If {full}, nothing happens."
                if other:
                    plain += f" Otherwise, it will {other}."
                if err and not _terminates(it.then):
                    note = "The code shows the message and then continues with the next step."
                    spec.intents.append((it, has_msg[0]))
                elif err:
                    note = "The message is followed by an exit, so processing stops here."
                    spec.intents.append((it, has_msg[0]))
            cat = "Validation" if (err or _sample_for(it.text) and not any(
                isinstance(s, Stmt) and s.kind in ("compute", "arith") for s in it.then)) else "Condition"
            if any(isinstance(s, Stmt) and s.kind in ("move", "compute", "arith") for s in it.then) and not err:
                cat = "Calculation" if any(isinstance(s, Stmt) and s.kind in ("compute", "arith") for s in it.then) else "Adjustment"
            rid = nid("BR")
            end = max(_block_lines(it))
            spec.rules.append(Rule(rid, cat, plain, example_for_if(it, prog), conf,
                                   (it.line, end), f"IF {it.text}", note,
                                   facts={"kind": "condition", "program": prog.name,
                                          "conditions": cond_facts(it.text, prog),
                                          "context": [cond_facts(c[1].text, prog) for c in ctx if c[0] == "if"],
                                          "actions": act_facts(it.then), "else_actions": act_facts(it.other)}))
            spec.covered.update(_block_lines(it))
            if depth == 0:
                step[0] += 1
                spec.flow.append((str(step[0]), f"Check whether {cond} ({rid}).", it.line))
        elif isinstance(it, Block) and it.kind == "eval":
            tid = nid("DT")
            subject = _subject_english(it.text, it, prog)
            rows, ex_rows = [], []
            targets = set()
            for w, ln, body in it.cases:
                label = _when_label(w, it, prog)
                out = _actions_english(body, prog) or "no action is coded"
                rows.append((label, out, ln))
                for s in body:
                    if isinstance(s, Stmt) and s.kind == "move":
                        targets.add(s.target)
                        ex_rows.append((label, s.target, s.value))
            has_other = any(w.upper() == "OTHER" for w, _, _ in it.cases)
            default = ("Covered by WHEN OTHER." if has_other else
                       "Not defined: any value not listed falls through with no action, so the "
                       "result keeps whatever value it had before.")
            kind = _classify(it, prog, spec)
            end = max(_block_lines(it))
            if it.text.upper() == "TRUE":
                subj_fields, _ = _flag_fields([w for w, _, _ in it.cases if w.upper() != "OTHER"], prog)
            else:
                subj_fields = [it.text.upper()]
            raw_rows = []
            for w, ln, body in it.cases:
                key = w.strip("'\"").upper()
                if it.text.upper() == "TRUE":
                    key = _flag_fields([w], prog)[1][0] if w.upper() != "OTHER" else "OTHER"
                raw_rows.append({"key": key, "line": ln, "actions": act_facts(body)})
            tfacts = {"kind": "table", "program": prog.name, "table_id": tid, "subject": it.text.upper(),
                      "fields": subj_fields, "rows": raw_rows, "has_default": has_other}
            spec.tables.append(Table(tid, subject, kind, rows, default, (it.line, end),
                                     f"EVALUATE {it.text}", example_for_table(ex_rows, subject), facts=tfacts))
            # one BR rule per table as well, so the rules list is complete on its own
            rid = nid("BR")
            lead = f"When {pre}, the" if pre else "The"
            summary = "; ".join(f"{lab} → {out}" for lab, out, _ in rows)
            spec.rules.append(Rule(rid, "Decision", f"{lead} program decides by {subject} "
                                   f"(see table {tid}): {summary}.", example_for_table(ex_rows, subject),
                                   "confirmed", (it.line, end), f"EVALUATE {it.text}",
                                   "" if has_other else "No default (WHEN OTHER) branch.", facts=tfacts))
            spec.covered.update(_block_lines(it))
            if depth == 0:
                step[0] += 1
                spec.flow.append((str(step[0]), f"Decide the outcome by {subject} ({tid}).", it.line))
        elif isinstance(it, Stmt) and depth == 0:
            step[0] += 1
            text = action_english(it, prog)
            spec.flow.append((str(step[0]), text[0].upper() + text[1:] + ".", it.line))
            if it.kind in ("compute", "arith", "move", "call", "perform"):
                rid = nid("BR")
                cat = "Calculation" if it.kind in ("compute", "arith") else "Processing step"
                spec.rules.append(Rule(rid, cat, f"The program will always {text}.",
                                       "", "confirmed", (it.line, it.line), it.text,
                                       facts={"kind": "statement", "program": prog.name,
                                              "actions": act_facts([it])}))
            spec.covered.add(it.line)

    for p in prog.paras:
        if p.para != "(MAIN)" or p.then:
            if p.para != "(MAIN)":
                step[0] += 1
                spec.flow.append((str(step[0]), f"Start step \"{_para_english(p.para)}\".", p.line))
        _walk(p.then, visit)

    # inferred business intent: what a message-only check is probably meant to do
    for blk, msg in spec.intents:
        cond = _cond_english(blk.text, prog)
        review = re.search(r"REVIEW|REFER|APPROV|CHECK", msg.value, re.I)
        intent = "referred for manual review" if review else "rejected"
        if _terminates(blk.then):
            text = (f"When {cond}, the transaction is rejected (based on the message "
                    f"\"{msg.value}\"; the program stops at this point).")
        else:
            text = (f"When {cond}, the transaction is probably meant to be {intent} (based on the "
                    f"message \"{msg.value}\"). The code does not enforce this: it only shows the "
                    f"message and carries on.")
        spec.rules.append(Rule(nid("BR"), "Inferred intent", text, "", "inferred",
            (blk.line, msg.line), f"IF {blk.text} / DISPLAY '{msg.value}'",
            "Confirm with the business owner; see Gaps and contradictions."))
    # order everything from the beginning of the program to the end; an inferred-intent
    # rule sits directly after the confirmed rule it interprets
    order = {"Inferred intent": 1}
    spec.rules.sort(key=lambda r: (r.lines[0], order.get(r.category, 0)))
    remap = {}
    for i, r in enumerate(spec.rules, 1):
        remap[r.id] = f"BR-{i:02d}"
    for r in spec.rules:
        r.id = remap[r.id]
    spec.flow = [(no, re.sub(r"\bBR-\d+\b", lambda m: remap.get(m.group(0), m.group(0)), t), ln)
                 for no, t, ln in spec.flow]
    _crosscheck(spec)
    return spec


def _subject_english(text: str, blk: Block | None = None, prog: Program | None = None) -> str:
    if text.upper() != "TRUE":
        return field_english(text)
    if blk is not None and blk.cases:
        names = [w for w, _, _ in blk.cases if w.upper() != "OTHER"]
        heads = {n.upper().split("-")[0] for n in names if re.match(r"^[A-Z0-9-]+$", n, re.I)}
        if len(heads) == 1 and len(names) > 1:
            return field_english(heads.pop())
    return "which condition applies"


def _when_label(w: str, blk: Block, prog: Program) -> str:
    if w.upper() == "OTHER":
        return "any other value"
    if blk.text.upper() == "TRUE":
        if re.match(r"^[A-Z0-9-]+$", w, re.I):
            parts = w.upper().split("-")
            names = [x for x, _, _ in blk.cases if x.upper() != "OTHER"]
            heads = {n.upper().split("-")[0] for n in names if re.match(r"^[A-Z0-9-]+$", n, re.I)}
            if len(heads) == 1 and len(parts) > 1:
                return field_english("-".join(parts[1:]))
            return field_english(w)
        return _cond_english(w, prog)
    return value_english(w)


def _classify(blk: Block, prog: Program, spec: Spec) -> str:
    """STATE MACHINE only if the evaluated field is itself written by the program
    (i.e. its value moves between states); otherwise it is a LOOKUP TABLE."""
    subj = blk.text.upper()
    watched = {subj} if subj != "TRUE" else set()
    if subj == "TRUE":
        for w, _, _ in blk.cases:
            if w.upper() in prog.flags:
                watched.add(prog.flags[w.upper()][0])
    return "State machine" if any(f in spec.writes for f in watched) else "Lookup table"


# --------------------------------------------------------------------------
# Cross-checks: gaps and contradictions (deterministic, no LLM)
# --------------------------------------------------------------------------
def _crosscheck(spec: Spec) -> None:
    prog = spec.program
    n = [0]

    def add(kind, sev, text, lines, question):
        n[0] += 1
        spec.findings.append(Finding(f"GC-{n[0]:02d}", kind, sev, text, sorted(set(lines)), question))

    ifs: list[Block] = []
    evals: list[Block] = []

    def collect(it, d, c):
        if isinstance(it, Block) and it.kind == "if":
            ifs.append(it)
        elif isinstance(it, Block) and it.kind == "eval":
            evals.append(it)
    for p in prog.paras:
        _walk(p.then, collect)

    # 1. values handled by a decision table but excluded by an earlier check
    for ev in evals:
        if ev.text.upper() == "TRUE":
            continue
        fld = ev.text.upper()
        for g in ifs:
            if g.line >= ev.line:
                continue
            clauses = re.split(r"\s+AND\s+", g.text, flags=re.I)
            neq = [c for c in clauses if (m := _CMP1.match(c)) and m.group(1).upper() == fld
                   and " ".join(m.group(2).upper().split()) == "NOT ="]
            if len(neq) != len(clauses) or not neq:
                continue
            allowed = {_CMP1.match(c).group(3).strip().strip("'\"").upper() for c in neq}
            for w, ln, _ in ev.cases:
                val = w.strip("'\"").upper()
                if w.upper() == "OTHER" or val in allowed:
                    continue
                stops = _terminates(g.then)
                if stops:
                    add("Unreachable code", "medium",
                        f"The {field_english(fld)} {value_english(w)} has an entry in decision table "
                        f"(line {ln}), but the earlier check on line {g.line} only allows "
                        f"{', '.join(sorted(allowed))} and exits the program otherwise, so this entry "
                        f"can never be used.", [g.line, ln],
                        f"Should {value_english(w)} be supported (relax the check on line {g.line}) or "
                        f"should the table entry be removed?")
                else:
                    add("Contradiction", "high",
                        f"The {field_english(fld)} {value_english(w)} is flagged as not supported by "
                        f"the check on line {g.line}, yet the decision table on line {ln} still gives it "
                        f"a value. Because that check only shows a message and does not stop processing, "
                        f"a {value_english(w)} payment would carry on and be processed anyway.",
                        [g.line, ln],
                        f"Is {value_english(w)} meant to be supported? If not, should the check on "
                        f"line {g.line} stop processing?")

    # 2. checks with no outcome / no effect
    for g in ifs:
        if not g.then and not g.other:
            add("Missing outcome", "medium",
                f"The check on line {g.line} ({_cond_english(g.text, prog)}) has no action coded.",
                [g.line], "What should happen when this condition holds?")
        elif all(isinstance(s, Stmt) and s.kind == "continue" for s in g.then) and not g.other:
            add("Check has no effect", "medium",
                f"The check on line {g.line} ({_cond_english(g.text, prog)}) only says CONTINUE, so "
                f"records that fail it are processed exactly like records that pass it.",
                [g.line], "Was this check meant to stop or route non-matching records?")

    # 3. error messages that do not stop processing
    for g in ifs:
        msgs = [s for s in g.then if isinstance(s, Stmt) and s.kind == "display"]
        if msgs and not _terminates(g.then):
            add("Validation does not stop processing", "high",
                f"When {_cond_english(g.text, prog)}, the program shows \"{msgs[0].value}\" (line "
                f"{msgs[0].line}) but carries on with the remaining steps.",
                [g.line, msgs[0].line],
                ("Should this condition route the transaction for review before it continues?"
                 if re.search(r"REVIEW|REFER|APPROV", msgs[0].value, re.I) else
                 "Should this condition reject the transaction and stop further processing?"))

    # 4. overlapping numeric thresholds on the same field
    ranges: dict[str, list[tuple[str, float, Block]]] = {}
    for g in ifs:
        m = _CMP1.match(g.text)
        if m and (v := _num(m.group(3))) is not None and m.group(2) in (">", ">="):
            ranges.setdefault(m.group(1).upper(), []).append((m.group(2), v, g))
    for fld, rs in ranges.items():
        rs.sort(key=lambda r: r[1])
        for lo, hi in zip(rs, rs[1:]):
            low_blk, high_blk = lo[2], hi[2]
            first = low_blk if low_blk.line < high_blk.line else high_blk
            if _terminates(first.then):
                continue
            add("Overlapping thresholds", "low",
                f"A {field_english(fld)} above {_money(hi[1])} meets both the check on line "
                f"{high_blk.line} and the check on line {low_blk.line}, so both outcomes apply. "
                f"Effective bands: up to {_money(lo[1])} → neither; {_money(lo[1])}–{_money(hi[1])} → "
                f"line {low_blk.line} only; above {_money(hi[1])} → both.",
                [low_blk.line, high_blk.line],
                "Is it intended that the largest amounts trigger both outcomes?")

    # 5. data flow: inputs with no visible source, used-before-set, unused results
    no_source, before_set = [], []
    for f, where in sorted(spec.reads.items()):
        if f in prog.flags or f not in prog.data:
            continue
        d = prog.data[f]
        if d["value"] is not None or d["section"] not in ("WORKING-STORAGE", "LOCAL-STORAGE", ""):
            continue
        writes = spec.writes.get(f, [])
        if not writes:
            no_source.append(f)
        elif min(where) < min(writes):
            before_set.append((f, min(where), min(writes)))
    if no_source:
        add("Inputs with no visible source", "medium",
            "These values are read but never set in this program and have no starting value: "
            + ", ".join(f"{field_english(f)} ({f})" for f in no_source)
            + ". They must be filled by another program, a file read or a copybook.",
            [spec.reads[f][0] for f in no_source],
            "Which upstream program or file supplies each of these values?")
    unused = [f for f, w in spec.writes.items() if f not in spec.reads
              and prog.data.get(f, {}).get("section") in ("WORKING-STORAGE", "LOCAL-STORAGE")]
    for f, first_read, first_write in before_set:
        add("Value checked before it is calculated", "high",
            f"The {field_english(f)} ({f}) is checked on line {first_read}, but nothing calculates it "
            f"beforehand; the first place it is set is line {first_write}.",
            [first_read, first_write],
            f"Where should the {field_english(f)} be calculated before line {first_read}?")
        stem = f.split("-")[-2] if f.count("-") >= 2 else f.split("-")[0]
        partners = [u for u in unused if stem in u.split("-")]
        if partners:
            amt = next((r for r in spec.reads if r in prog.data and r.endswith("AMT") and r != f), None)
            formula = (f"{field_english(f)} = {field_english(amt)} × {field_english(partners[0])}"
                       if amt else f"{field_english(f)} from {field_english(partners[0])}")
            add("Likely missing calculation", "high",
                f"The {field_english(partners[0])} ({partners[0]}) is looked up but never used, and the "
                f"{field_english(f)} is never calculated. The code appears to be missing a step such as "
                f"\"{formula}\".", spec.writes[partners[0]] + [first_read],
                f"Confirm the intended formula for the {field_english(f)} and where it belongs.")
            unused = [u for u in unused if u != partners[0]]
    for f in unused:
        where = spec.writes[f]
        add("Result never used", "medium",
            f"The {field_english(f)} ({f}) is set on line(s) {', '.join(map(str, sorted(set(where))))} "
            f"but never used afterwards in {prog.name}.",
            list(where), f"Is {f} meant to feed a calculation or an output that is missing?")

    # 6. decision tables without a default
    for ev in evals:
        if not any(w.upper() == "OTHER" for w, _, _ in ev.cases):
            add("No default case", "low",
                f"The decision by {_subject_english(ev.text, ev, prog)} on line {ev.line} has no "
                f"'any other value' branch; unlisted values receive no outcome.",
                [ev.line], "What should happen for values not listed in the table?")

    # 7. hard-coded business constants
    seen = set()
    for g in ifs:
        for v in re.findall(r"(?<![\w-])(\d+\.\d+|\d{3,})(?![\w-])", g.text):
            if v in seen:
                continue
            seen.add(v)
            add("Hard-coded limit", "low",
                f"The value {v} in the check on line {g.line} is written into the code.",
                [g.line], f"Is {v} a business limit that should be configurable, and who owns it?")


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
_TAG = {"confirmed": "✅ Confirmed", "inferred": "🟡 Inferred", "gap": "⛔ Gap"}


def _cell(s: str) -> str:
    return (s or "—").replace("|", "\\|").replace("\n", " ")


def _src(prog: Program, a: int, b: int) -> str:
    return f"{prog.path}:{a}" + (f"-{b}" if b != a else "")


def coverage(spec: Spec) -> tuple[int, int, list[int]]:
    total = spec.program.exec_lines
    missing = sorted(total - spec.covered)
    return len(total) - len(missing), len(total), missing


def render_rules(specs: list[Spec]) -> str:
    """BA-facing rules document (tables, plain English, gaps up front)."""
    out = ["# Domain rules\n",
           "_Every rule is written in plain business language. The code it came from is kept "
           "under **Technical detail** for developers. Field names such as \"payment amount\" are "
           "derived from the program's own naming._\n"]
    for sp in specs:
        p = sp.program
        cov, tot, _ = coverage(sp)
        out.append(f"\n## {p.name}\n")
        out.append(f"**Coverage:** {cov} of {tot} executable statements are explained by a rule "
                   f"({(100 * cov // tot) if tot else 100}%).\n")
        out.append("\n### Business rules\n")
        out.append("| ID | Type | Rule | Example | Confidence | Source |")
        out.append("|---|---|---|---|---|---|")
        for r in sp.rules:
            plain = r.plain + (f" _Note: {r.note}_" if r.note else "")
            out.append(f"| {r.id} | {r.category} | {_cell(plain)} | {_cell(r.example)} | "
                       f"{_TAG[r.confidence]} | {_src(p, *r.lines)} |")
        for t in sp.tables:
            out.append(f"\n### {t.id} — decision by {t.subject} ({t.kind})\n")
            out.append(f"| When the {t.subject} is | Then the program will |")
            out.append("|---|---|")
            for lab, res, ln in t.rows:
                out.append(f"| {_cell(lab)} | {_cell(res)} |")
            out.append(f"| _any other value_ | _{t.default}_ |" if "Not defined" in t.default else "")
            if t.example:
                out.append(f"\n_Example (illustrative):_ {t.example}")
        out.append("\n### Gaps and contradictions\n")
        out.append(_render_findings(sp) or "_No gaps or contradictions detected by the automated "
                   "checks. Manual review is still recommended._")
        out.append("\n<details><summary>Technical detail</summary>\n")
        for r in sp.rules:
            out.append(f"- **{r.id}** `{r.technical}` — {_src(p, *r.lines)}")
        out.append("\n</details>")
    out.append("\n**Legend:** ✅ Confirmed — read directly from the code · 🟡 Inferred — business "
               "meaning deduced, not stated in code · ⛔ Gap — cannot be determined, needs an owner\n")
    return "\n".join(x for x in out if x is not None)


def _render_findings(sp: Spec) -> str:
    if not sp.findings:
        return ""
    rows = ["| ID | Type | Severity | Finding | Question for the business | Lines |",
            "|---|---|---|---|---|---|"]
    for f in sorted(sp.findings, key=lambda f: {"high": 0, "medium": 1, "low": 2}[f.severity]):
        rows.append(f"| {f.id} | {f.kind} | {f.severity.title()} | {_cell(f.text)} | "
                    f"{_cell(f.question)} | {', '.join(map(str, f.lines))} |")
    return "\n".join(rows)


def render_gaps(specs: list[Spec]) -> str:
    out = ["# Gaps and contradictions\n",
           "_Produced by deterministic cross-checks over the extracted rules, not by an AI's "
           "judgement, so an empty section means the checks ran and found nothing._\n"]
    for sp in specs:
        out.append(f"\n## {sp.program.name}\n")
        out.append(_render_findings(sp) or "_No gaps or contradictions detected by the automated "
                   "checks. Manual review is still recommended._")
        cov, tot, missing = coverage(sp)
        if missing:
            out.append(f"\n**Unexplained statements (coverage gap):** lines {', '.join(map(str, missing))}")
    return "\n".join(out)


def render_process(specs: list[Spec]) -> str:
    """Business-readable process view: overview first, then steps, then the decisions."""
    out = ["# Process\n",
           "_Starts with what the program does, then walks through its steps from beginning to "
           "end. Code references are at the end of each program's section._\n"]
    for sp in specs:
        p = sp.program
        out.append(f"\n## {p.name}\n")
        out.append(_purpose(sp) + "\n")
        out.append("\n### Steps, from beginning to end\n")
        for no, text, ln in sp.flow:
            out.append(f"{no}. {text}")
        for t in sp.tables:
            out.append(f"\n### How the {t.subject} decides the outcome ({t.id})\n")
            out.append(f"| When the {t.subject} is | Then the program will |")
            out.append("|---|---|")
            for lab, res, ln in t.rows:
                out.append(f"| {_cell(lab)} | {_cell(res)} |")
            if t.example:
                out.append(f"\n_Example (illustrative):_ {t.example}")
        out.append("\n<details><summary>Technical detail</summary>\n")
        for no, text, ln in sp.flow:
            code = p.lines[ln - 1].strip() if 0 < ln <= len(p.lines) else ""
            out.append(f"- Step {no}: `{code}` — {p.path}:{ln}")
        out.append("\n</details>")
    return "\n".join(out)


def render_ops_spec(specs: list[Spec]) -> str:
    """Layered operational specification: generic → specific."""
    out = ["# Detailed operational specification\n",
           "_Read top-down: each level adds detail to the one before. Business readers can stop "
           "after Level 3; analysts after Level 5; developers use Level 7._\n"]
    for sp in specs:
        p = sp.program
        cov, tot, missing = coverage(sp)
        inputs = sorted(f for f in sp.reads if f not in sp.writes and f in p.data)
        outputs = sorted(f for f in sp.writes)
        checks = [r for r in sp.rules if r.category in ("Validation", "Condition")]
        calcs = [r for r in sp.rules if r.category in ("Calculation", "Adjustment")]
        out.append(f"\n## {p.name}\n")

        out.append("\n### Level 1 — What this program does\n")
        purpose = _purpose(sp)
        out.append(purpose)
        out.append(f"\nIt applies **{len(checks)} check(s)**, **{len(sp.tables)} decision table(s)** and "
                   f"**{len(calcs)} calculation/adjustment rule(s)**. "
                   f"{len(sp.findings)} gap(s)/contradiction(s) were found (Level 6).\n")

        out.append("\n### Level 2 — Inputs and outputs\n")
        out.append("| Direction | Business name | Field |")
        out.append("|---|---|---|")
        for f in inputs:
            out.append(f"| Input (read, not set here) | {field_english(f)} | `{f}` |")
        for f in outputs:
            out.append(f"| Output / result (set here) | {field_english(f)} | `{f}` |")

        out.append("\n### Level 3 — Processing flow (in execution order)\n")
        for no, text, ln in sp.flow:
            out.append(f"{no}. {text}")

        out.append("\n### Level 4 — Business rules in detail\n")
        for r in sp.rules:
            out.append(f"**{r.id} · {r.category}** — {_TAG[r.confidence]}  ")
            out.append(f"{r.plain}  ")
            if r.example:
                out.append(f"_Example (illustrative):_ {r.example}  ")
            if r.note:
                out.append(f"_Note:_ {r.note}  ")
            out.append(f"_Source:_ `{_src(p, *r.lines)}`\n")

        out.append("\n### Level 5 — Decision tables\n")
        if not sp.tables:
            out.append("_None._")
        for t in sp.tables:
            out.append(f"\n**{t.id} — by {t.subject}** · {t.kind} · `{_src(p, *t.lines)}`\n")
            out.append(f"| When the {t.subject} is | Then | Line |")
            out.append("|---|---|---|")
            for lab, res, ln in t.rows:
                out.append(f"| {_cell(lab)} | {_cell(res)} | {ln} |")
            out.append(f"\n_Values not listed:_ {t.default}")
            if t.example:
                out.append(f"\n_Example (illustrative):_ {t.example}")
            if t.kind == "Lookup table":
                out.append("\n_Lookup table: returns a value by key; nothing changes state over time._")

        out.append("\n### Level 6 — Gaps and contradictions\n")
        out.append(_render_findings(sp) or "_None detected by the automated checks._")

        out.append("\n### Level 7 — Technical traceability\n")
        out.append(f"**Coverage:** {cov}/{tot} executable statements explained "
                   f"({(100 * cov // tot) if tot else 100}%)."
                   + (f" Unexplained lines: {', '.join(map(str, missing))}." if missing else ""))
        out.append("\n| ID | Code | Lines |")
        out.append("|---|---|---|")
        for r in sp.rules:
            out.append(f"| {r.id} | `{_cell(r.technical)}` | {_src(p, *r.lines)} |")
        for t in sp.tables:
            out.append(f"| {t.id} | `{_cell(t.technical)}` | {_src(p, *t.lines)} |")
        out.append("\n| Field | Business name | Set at | Used at |")
        out.append("|---|---|---|---|")
        for f in sorted(set(sp.reads) | set(sp.writes)):
            if f not in p.data:
                continue
            out.append(f"| `{f}` | {field_english(f)} | "
                       f"{', '.join(map(str, sorted(set(sp.writes.get(f, []))))) or '—'} | "
                       f"{', '.join(map(str, sorted(set(sp.reads.get(f, []))))) or '—'} |")
    return "\n".join(out)


def _purpose(sp: Spec) -> str:
    p = sp.program
    outputs = [field_english(f) for f in sp.writes]
    checks = [r for r in sp.rules if r.category in ("Validation", "Condition")]
    bits = []
    if checks:
        bits.append(f"checks the incoming record against {len(checks)} condition(s)")
    if sp.tables:
        bits.append("looks up " + " and ".join(
            _table_output(t, sp) for t in sp.tables))
    if outputs:
        bits.append("produces the " + ", ".join(dict.fromkeys(outputs)))
    body = ", ".join(bits) if bits else "runs a sequence of processing steps"
    return f"**{p.name}** {body}. _(Summary generated from the code structure.)_"


def _table_output(t: Table, sp: Spec) -> str:
    m = re.search(r"the ([a-z ]+?) (?:to|as)", t.rows[0][1]) if t.rows else None
    what = m.group(1) if m else "an outcome"
    return f"the {what} by {t.subject}"


# --------------------------------------------------------------------------
# Optional AI rewriting pass (used only when an AI backend is configured)
# --------------------------------------------------------------------------
REWRITE_PROMPT = ("Rewrite the rules , processes , gaps and contradictions ops specs , full "
                  "document  as a single sentence a non-technical business analyst would understand. "
                  "State the condition and the outcome for all the 5 ( rules, ops specs, processes, "
                  "full documents , gaps and contradictions)  in business terms (not variable names). "
                  "Then give one worked numeric example. Do not use code syntax. give the details in "
                  "the end and start with generic at the beginning")

REWRITE_SYSTEM = (REWRITE_PROMPT + "\n\nYou will receive JSON with the program's processing steps "
                  "and rules, already in execution order (beginning to end), each with an id, the "
                  "code it came from and a draft sentence. Rewrite each one, keeping the same ids and "
                  "the same order. Keep every number, limit, rate, currency and message text exactly "
                  "as given. Do not add facts that are not in the code. Technical details are kept "
                  "separately at the end of the document, so leave code out of your sentences. Reply "
                  "with JSON only: {\"processes\": [{\"id\": \"P-1\", \"step\": \"...\"}], "
                  "\"rules\": [{\"id\": \"BR-01\", \"rule\": \"...\", \"example\": \"...\"}], "
                  "\"findings\": [{\"id\": \"GC-01\", \"finding\": \"...\", \"question\": \"...\", "
                  "\"example\": \"...\"}]}")


def _must_keep(r: Rule) -> list[str]:
    """Literals from the code that a rewrite must preserve (numbers and quoted values)."""
    src = r.technical + " " + r.plain
    keep = [q.strip() for q in re.findall(r"'([^']+)'", r.technical)]
    for n in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", r.technical):
        if n not in ("0", "1"):
            keep.append(n)
    return keep


def _survives(literal: str, text: str) -> bool:
    if literal.lower() in text.lower():
        return True
    n = _num(literal)
    if n is None:
        return False
    variants = {literal, f"{n:,.2f}", f"{n:,.0f}" if n == int(n) else literal, f"{n:g}",
                f"{n * 100:.2f}%", f"{n * 100:g}%"}
    return any(v in text for v in variants)


def rewrite_rules(spec: Spec, call) -> int:
    """Rewrite each rule with REWRITE_PROMPT via call(system, user) -> str.
    A rewrite is accepted only if every literal from the code survives it; otherwise the
    deterministic wording is kept. Returns the number of rules rewritten."""
    import json
    from .llm.base import strip_json as parse_json
    rules = [r for r in spec.rules]
    if not rules:
        return 0
    payload = [{"id": r.id, "type": r.category, "code": r.technical,
                "draft": r.plain, "draft_example": r.example} for r in rules]
    procs = [{"id": f"P-{no}", "draft": text,
              "code": spec.program.lines[ln - 1].strip() if 0 < ln <= len(spec.program.lines) else ""}
             for no, text, ln in spec.flow]
    try:
        finds = [{"id": f.id, "type": f.kind, "draft": f.text, "question": f.question,
                  "lines": f.lines} for f in spec.findings]
        reply = call(REWRITE_SYSTEM, json.dumps({"program": spec.program.name,
                                                 "processes": procs, "rules": payload,
                                                 "findings": finds}))
        data = parse_json(reply)
    except Exception:
        return 0
    by_id = {x.get("id"): x for x in (data or {}).get("rules", []) if isinstance(x, dict)}
    p_by_id = {x.get("id"): x for x in (data or {}).get("processes", []) if isinstance(x, dict)}
    done = 0
    new_flow = []
    for no, text, ln in spec.flow:
        new = p_by_id.get(f"P-{no}")
        keep = re.findall(r"\b(?:BR|DT)-\d+\b", text) + re.findall(r'"([^"]+)"', text) + \
            [n for n in re.findall(r"(?<![\w.])(\d+(?:[.,]\d+)*)(?![\w.])", text) if n not in ("0", "1")]
        if new and new.get("step") and all(_survives(k, new["step"]) for k in keep):
            new_flow.append((no, new["step"].strip(), ln))
            done += 1
        else:
            new_flow.append((no, text, ln))
    spec.flow = new_flow
    f_by_id = {x.get("id"): x for x in (data or {}).get("findings", []) if isinstance(x, dict)}
    for f in spec.findings:
        new = f_by_id.get(f.id)
        if not new or not new.get("finding"):
            continue
        keep = re.findall(r'"([^"]+)"', f.text) + \
            [n for n in re.findall(r"(?<![\w.])(\d+(?:[.,]\d+)*)(?![\w.])", f.text)
             if n not in ("0", "1") and not any(str(l) == n for l in f.lines)]
        text = new["finding"].strip() + (f" Example: {new['example'].strip()}" if new.get("example") else "")
        if all(_survives(k, text) for k in keep):
            f.text = text
            f.question = (new.get("question") or f.question).strip()
            done += 1
    for r in rules:
        new = by_id.get(r.id)
        if not new or not new.get("rule"):
            continue
        text = f"{new.get('rule', '')} {new.get('example', '')}"
        if all(_survives(k, text) for k in _must_keep(r)):
            r.note = (r.note + " " if r.note else "") + f"Original wording: {r.plain}"
            r.plain = new["rule"].strip()
            r.example = (new.get("example") or r.example).strip()
            done += 1
    return done


# --------------------------------------------------------------------------
# Claims for the Reversa registry (so scoring/reviewer keep working)
# --------------------------------------------------------------------------
def to_json(specs: list[Spec]) -> dict[str, Any]:
    """Full machine-readable output: every rule, table, gap and coverage figure."""
    progs = []
    for sp in specs:
        p = sp.program
        cov, tot, missing = coverage(sp)
        progs.append({
            "program": p.name, "file": p.path,
            "coverage": {"explained": cov, "total": tot, "unexplained_lines": missing},
            "rules": [{"id": r.id, "type": r.category, "rule": r.plain, "example": r.example,
                       "confidence": r.confidence, "lines": list(r.lines), "code": r.technical,
                       "note": r.note, "facts": r.facts} for r in sp.rules],
            "decision_tables": [{"id": t.id, "subject": t.subject, "kind": t.kind,
                                 "rows": [{"when": a, "then": b, "line": c} for a, b, c in t.rows],
                                 "default": t.default, "lines": list(t.lines), "facts": t.facts}
                                for t in sp.tables],
            "gaps_and_contradictions": [{"id": f.id, "type": f.kind, "severity": f.severity,
                                         "finding": f.text, "question": f.question, "lines": f.lines}
                                        for f in sp.findings],
            "process_flow": [{"step": no, "text": t, "line": ln} for no, t, ln in sp.flow],
        })
    return {"generator": "reversa-specbuilder", "programs": progs}


def to_claims(sp: Spec) -> list[dict[str, Any]]:
    p = sp.program
    claims = []
    for r in sp.rules:
        a, b = r.lines
        claims.append({
            "kind": "rule" if r.category != "Decision" else "behavior",
            "confidence": r.confidence,
            "statement": f"[{r.id}] {r.plain}",
            "evidence": [{"file": p.path, "line_start": a, "line_end": b,
                          "excerpt": "\n".join(p.lines[a - 1:b]).strip()[:400]}],
            "notes": f"Technical: {r.technical}." + (f" Example: {r.example}" if r.example else "")
                     + (f" {r.note}" if r.note else ""),
        })
    return claims


def to_gaps(sp: Spec) -> list[dict[str, Any]]:
    sev = {"high": "critical", "medium": "moderate", "low": "cosmetic"}
    return [{"description": f"[{f.id}] {f.kind}: {f.text}", "severity": sev[f.severity],
             "blocking": f.severity == "high"} for f in sp.findings]


def to_questions(sp: Spec) -> list[dict[str, Any]]:
    return [{"question": f"[{f.id}] {f.question}", "why_it_matters": f.text} for f in sp.findings]
