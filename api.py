"""
Reversa API — run reverse-documentation on a codebase and return a Word document.

POST /analyze            multipart: file=<zip>  OR  repo_url=<git url>
                         optional form fields: backend (heuristic|anthropic|qwen|hybrid-qwen|hybrid-anthropic),
                         target (e.g. go), title

hybrid-*: heuristic extraction; Qwen/Anthropic only for the plain-English rewrite and the
Business Context overview.
GET  /health

Local run:   uvicorn api:app --reload --port 8000
Render:      uvicorn api:app --host 0.0.0.0 --port $PORT
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import pypandoc
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import uuid
import json
from datetime import datetime

from reversa.docx_export import build_docx, ordered_markdown_files


def _docx_export_status() -> str:
    """'ok', or why the formatted Word export cannot run here. The exporter itself is pure
    Python; it only needs pandoc (bundled with pypandoc_binary) to read the Markdown."""
    try:
        pypandoc.get_pandoc_version()
        return "ok"
    except Exception as e:  # noqa: BLE001
        return (f"pandoc not available ({type(e).__name__}: {e}). Install it into the Python running "
                f"this server: {sys.executable} -m pip install pypandoc_binary==1.15")


DOCX_EXPORT_STATUS = _docx_export_status()
if DOCX_EXPORT_STATUS != "ok":
    print(f"WARNING: formatted Word export unavailable - {DOCX_EXPORT_STATUS}", file=sys.stderr)

# Saved runs: every analysis is kept here so it can be reloaded into the tabs instantly.
RUNS_DIR = Path(os.getenv("REVERSA_RUNS_DIR", str(Path.home() / ".reversa_runs")))


def _save_run(payload: dict, docx: Path, backend: str, title: str, source: str,
              xlsx: Optional[Path] = None) -> None:
    try:
        stamp = datetime.now()
        slug = re.sub(r"[^A-Za-z0-9]+", "-", Path(source).name or "run").strip("-")[:40] or "run"
        rid = f"{stamp:%Y%m%d-%H%M%S}-{backend}-{slug}"
        d = RUNS_DIR / rid
        d.mkdir(parents=True, exist_ok=True)
        meta = {"id": rid, "when": stamp.strftime("%d %b %Y, %H:%M"), "backend": backend,
                "title": title, "source": Path(source).name or source}
        body = {k: v for k, v in payload.items() if k != "id"}
        (d / "run.json").write_text(json.dumps({"meta": meta, **body}), encoding="utf-8")
        if docx.exists():
            shutil.copy(docx, d / "reversa_spec.docx")
        if xlsx and Path(xlsx).exists():
            shutil.copy(xlsx, d / "standards_comparison.xlsx")
    except Exception:
        pass   # saving is best-effort; never break an analysis because of it

app = FastAPI(title="Reversa API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
RUN_TIMEOUT_S = int(os.getenv("RUN_TIMEOUT_S", "900"))          # 15 min ceiling for reversa run
SDD_DIR = "_reversa_sdd"
BACKENDS = ("heuristic", "anthropic", "qwen", "hybrid-qwen", "hybrid-anthropic")
NEEDS_ANTHROPIC_KEY = ("anthropic", "hybrid-anthropic")
# Which LLM writes the Business Context overview for each backend. Backends not listed keep
# the existing behaviour: Anthropic if ANTHROPIC_API_KEY is set, otherwise no overview.
BUSINESS_CONTEXT_LLM = {"qwen": "qwen", "hybrid-qwen": "qwen", "hybrid-anthropic": "anthropic"}
# Reading order for the Word doc and preview: reversa.docx_export.ORDER


# ── helpers ──────────────────────────────────────────────────────────────────
def _safe_extract(zip_path: Path, dest: Path) -> None:
    """Extract a zip, refusing entries that escape dest (zip-slip)."""
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise HTTPException(400, f"Unsafe path in zip: {member.filename}")
        zf.extractall(dest)


def _project_root(extracted: Path) -> Path:
    """If the zip contained a single top-level folder, descend into it."""
    entries = [p for p in extracted.iterdir() if not p.name.startswith(("__MACOSX", "."))]
    return entries[0] if len(entries) == 1 and entries[0].is_dir() else extracted


def _run(cmd: list[str], cwd: Path, env: dict) -> str:
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                              timeout=RUN_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"reversa timed out after {RUN_TIMEOUT_S}s")
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout)[-3000:]
        raise HTTPException(500, f"{' '.join(cmd[-2:])} failed:\n{tail}")
    return proc.stdout


def _collect_markdown(sdd: Path, title: str) -> str:
    """Concatenate every .md under _reversa_sdd into one document, demoting headings."""
    files = ordered_markdown_files(sdd)
    if not files:
        raise HTTPException(500, f"reversa produced no Markdown under {SDD_DIR}")

    parts = [f"% {title}\n"]                     # pandoc title block → Word title
    for f in files:
        section = f.relative_to(sdd).with_suffix("").as_posix().replace("/", " › ")
        body = f.read_text(encoding="utf-8", errors="replace")
        body = re.sub(r"^(#{1,5})\s", lambda m: "#" * (len(m.group(1)) + 1) + " ", body, flags=re.M)
        parts.append(f"\n\n# {section}\n\n{body}")
    return "\n".join(parts)


def _to_docx(sdd: Path, markdown: str, out: Path, title: str) -> Optional[str]:
    """Styled Word document: title page, Contents, numbered sections, page numbers.
    Falls back to a plain pandoc conversion so a formatting problem never loses a run, and
    returns the reason (None when the formatted export worked) so the UI can show it."""
    try:
        build_docx(sdd, out, title=title)
        return None
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        reason = DOCX_EXPORT_STATUS if DOCX_EXPORT_STATUS != "ok" else f"{type(e).__name__}: {e}"
        print(f"warning: formatted Word export failed ({reason}); using plain export", file=sys.stderr)
        body = markdown.split("\n", 1)[1] if markdown.startswith("% ") else markdown
        # say so inside the file too, where it cannot be missed
        shown = reason.replace("`", "'")
        body = (f"> **This is the plain export.** The formatted export failed: `{shown}`. "
                f"Please report this message.\n\n") + body
        pypandoc.convert_text(
            body, "docx", format="gfm",
            outputfile=str(out),
            extra_args=["--toc", "--toc-depth=2", "--standalone", f"--metadata=title:{title}"],
        )
        return reason


def _to_html(markdown: str) -> str:
    return pypandoc.convert_text(markdown, "html", format="gfm",
                                 extra_args=["--toc", "--toc-depth=2"])


RESULTS: dict[str, Path] = {}          # job id → docx path (ephemeral; fine for a demo)

# Docs surfaced in the side panel for business readers: (tab title, candidate files
# in priority order — first match under _reversa_sdd wins).
PANEL_FILES = [
    ("Domain Rules", ["rules.md"]),
    ("Process", ["process_flow.md", "processes.md", "process.md"]),
    ("Gaps & Contradictions", ["gaps_contradictions.md"]),
    ("Detailed Ops Spec", ["ops_spec.md"]),
    ("Standards Comparison", ["comparison.md"]),
]
DEFAULT_STANDARDS = Path(__file__).parent / "standards" / "payments_fee_standard.json"
XLSX: dict[str, Path] = {}


def _panel_sections(sdd: Path) -> list[dict]:
    """Render the business-facing docs individually for the slide-over panel."""
    sections = []
    for tab_title, candidates in PANEL_FILES:
        for name in candidates:
            hits = sorted(sdd.rglob(name))
            if hits:
                body = hits[0].read_text(encoding="utf-8", errors="replace")
                sections.append({
                    "title": tab_title,
                    "file": hits[0].relative_to(sdd).as_posix(),
                    "html": pypandoc.convert_text(body, "html", format="gfm"),
                })
                break
    return sections


BUSINESS_PROMPT = """You are writing for bank business stakeholders (product owners, operations \
heads, risk managers) who will NOT read code. Below is a specification that was automatically \
extracted from a codebase.

Write a Business Context overview in plain, readable English with exactly these three short \
sections (no headings, just three paragraphs):
1. What the system does — describe the end-to-end behaviour in everyday business language.
2. Why it matters to the business — revenue, risk, customer/operational impact, as applicable.
3. What rules the code encodes — summarise the kinds of business rules recovered (limits, \
cut-offs, retries, reversals, duplicates, exceptions needing a human), and close by saying this \
document recovers those rules from the code so the business can confirm they are still the rules \
they want.

Ground every statement in the extracted spec below. Do not invent product names, numbers or \
rails that are not evidenced. If the spec is thin, stay general rather than fabricating. \
No code identifiers, no file paths, no bullet IDs. 150-250 words total.

Document title: {title}

Extracted specification:
{spec}"""


def _llm_business_context(md: str, title: str, backend: str = "heuristic") -> Optional[str]:
    """Synthesize a plain-English business overview from the extracted spec.
    qwen / hybrid-qwen use local Qwen (nothing leaves the machine); hybrid-anthropic uses the
    Anthropic API; other backends use the Anthropic API only if a key is set. Returns None
    (UI falls back to extracted files) if unavailable or failing."""
    from reversa.llm.prose import make_caller
    provider = BUSINESS_CONTEXT_LLM.get(backend)
    if provider is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return None
        provider = "anthropic"
    limit = 24000 if provider == "qwen" else 48000       # local models get a smaller context
    try:
        call = make_caller(provider, max_tokens=1024,
                           timeout=None if provider == "qwen" else 120)
        text = call("You write plain-English business summaries.",
                    BUSINESS_PROMPT.format(title=title, spec=md[:limit]))
        return text.strip() or None
    except Exception:
        return None


def _check_backend(backend: str) -> None:
    if backend not in BACKENDS:
        raise HTTPException(400, "backend must be one of: " + ", ".join(BACKENDS))
    if backend in NEEDS_ANTHROPIC_KEY and not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(400, "ANTHROPIC_API_KEY is not set on the server; use backend=heuristic "
                                 "or hybrid-qwen")


def _obtain_and_run(work: Path, file_bytes: Optional[bytes], repo_url: Optional[str],
                    backend: str, target: Optional[str], standards: Optional[Path] = None) -> Path:
    """Shared by /analyze and /analyze/preview: get code, run reversa, return _reversa_sdd."""
    src = work / "src"
    src.mkdir()
    if file_bytes is not None:
        if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(413, f"Upload exceeds {MAX_UPLOAD_MB} MB")
        zip_path = work / "upload.zip"
        zip_path.write_bytes(file_bytes)
        _safe_extract(zip_path, src)
    else:
        if not re.match(r"^https?://", repo_url or ""):
            raise HTTPException(400, "repo_url must be an http(s) git URL")
        _run(["git", "clone", "--depth", "1", repo_url, str(src)], cwd=work, env=os.environ.copy())
    project = _project_root(src)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    std = standards or (DEFAULT_STANDARDS if DEFAULT_STANDARDS.exists() else None)
    if std:
        env["REVERSA_STANDARDS"] = str(std)
    py = [sys.executable, "-m", "reversa"]
    _run(py + ["install"], cwd=project, env=env)
    run_cmd = py + ["run", "--backend", backend]
    if target:
        run_cmd += ["--target", target]
    _run(run_cmd, cwd=project, env=env)
    return project / SDD_DIR


INDEX_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Reversa — Legacy code → Specification</title>
<style>
 body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0;background:#0f1419;color:#e6edf3}
 header{padding:20px 32px;border-bottom:1px solid #263040;display:flex;align-items:center;gap:16px}
 header h1{font-size:20px;margin:0}header span{color:#8b98a5;font-size:13px}
 main{display:grid;grid-template-columns:340px 1fr;min-height:calc(100vh - 62px)}
 aside{padding:24px;border-right:1px solid #263040}
 label{display:block;font-size:12px;color:#8b98a5;margin:14px 0 6px;text-transform:uppercase;letter-spacing:.05em}
 input,select{width:100%;box-sizing:border-box;padding:10px;border-radius:6px;border:1px solid #334155;background:#161b22;color:#e6edf3}
 button{margin-top:18px;width:100%;padding:12px;border:0;border-radius:6px;background:#2f81f7;color:#fff;font-weight:600;cursor:pointer}
 button:disabled{background:#334155;cursor:wait}
 #dl{background:#238636;display:none}
 #status{margin-top:14px;font-size:13px;color:#8b98a5;white-space:pre-wrap}
 section{padding:32px 48px;overflow:auto}
 #out{max-width:900px}#out h1{border-bottom:1px solid #263040;padding-bottom:6px;margin-top:40px}
 #out pre{background:#161b22;padding:12px;border-radius:6px;overflow:auto}#out code{font-size:13px}
 #out table{border-collapse:collapse}#out td,#out th{border:1px solid #334155;padding:6px 10px}
 #out a{color:#58a6ff}.empty{color:#8b98a5;margin-top:80px;text-align:center}
 .tabbar{display:flex;gap:6px;margin:0 0 22px;border-bottom:1px solid #263040}
 .tabbar button{width:auto;margin:0;padding:9px 18px;font-size:13px;font-weight:600;background:transparent;border:0;border-bottom:2px solid transparent;color:#8b98a5;border-radius:0;cursor:pointer}
 .tabbar button:hover{color:#e6edf3}
 .tabbar button.active{color:#e6edf3;border-bottom-color:#2f81f7}
 .srcnote{font-size:11px;color:#8b98a5;margin:0 0 16px}
 .replay{font-size:12px;color:#e6edf3;background:#1f2a37;border-left:3px solid #2f81f7;padding:8px 12px;margin:0 0 14px}
</style></head><body>
<header><h1>Reversa</h1><span>Reverse documentation engineering — upload a legacy codebase, get a traceable operational specification</span></header>
<main>
<aside>
 <label>Codebase (zip)</label><input type="file" id="file" accept=".zip">
 <label>…or public git URL</label><input type="text" id="repo" placeholder="https://github.com/org/legacy-app">
 <label>Backend</label><select id="backend"><option value="heuristic">heuristic (offline, fast)</option><option value="anthropic">anthropic (LLM agents)</option><option value="qwen">qwen (local LLM)</option><option value="hybrid-qwen">hybrid · heuristic + local Qwen wording</option><option value="hybrid-anthropic">hybrid · heuristic + Anthropic wording</option></select>
 <label>Migration target (optional)</label><input type="text" id="target" placeholder="e.g. go, java, python">
 <label>Standard rules (JSON, optional)</label><input type="file" id="std" accept=".json">
 <label>Document title</label><input type="text" id="title" value="Operational Specification">
 <button id="go">Analyse</button>
 <button id="dl">Download Word document</button>
 <button id="xl" style="display:none">Export comparison to Excel</button>
 <div id="status"></div>
 <label>Saved runs</label><select id="runs"><option value="">— none yet —</option></select>
 <button id="load">Load saved run</button>
</aside>
<section><div id="out"><p class="empty">The specification will appear here.</p></div></section>
</main>
<script>
const $=id=>document.getElementById(id);let jobId=null;let fullHtml='';let sections=[];let tabs=[];let active=0;let replay='';
function _top(){const s=document.querySelector('section');if(s)s.scrollTop=0;}
function buildTabs(){
  const sc=sections.filter(x=>x.title==='Standards Comparison');
  tabs=sections.filter(x=>x.title!=='Standards Comparison').concat([{title:'Full Document',file:'',html:fullHtml}]).concat(sc);
  active=0;renderTab();
}
function renderTab(){
  const bar='<div class="tabbar">'+tabs.map((t,i)=>'<button class="'+(i===active?'active':'')+'" onclick="setTab('+i+')">'+t.title+'</button>').join('')+'</div>';
  const t=tabs[active];
  const src=t.file?'<div class="srcnote">source: '+t.file+' &middot; extracted from the code by Reversa</div>':'';
  const rb=replay?'<div class="replay">'+replay+'</div>':'';
  $('out').innerHTML=bar+rb+src+t.html;_top();
}
function setTab(i){active=i;renderTab();}
$('go').onclick=async()=>{
  const fd=new FormData();const f=$('file').files[0];
  if(f)fd.append('file',f);else if($('repo').value.trim())fd.append('repo_url',$('repo').value.trim());
  else{ $('status').textContent='Choose a zip or enter a git URL.';return; }
  fd.append('backend',$('backend').value);fd.append('title',$('title').value||'Operational Specification');
  if($('target').value.trim())fd.append('target',$('target').value.trim());
  const sf=$('std').files[0];if(sf)fd.append('standards',sf);
  $('go').disabled=true;$('dl').style.display='none';$('status').textContent='Running reversa… this can take up to a minute.';
  try{
    const r=await fetch('/analyze/preview',{method:'POST',body:fd});
    if(!r.ok){$('status').textContent='Error: '+(await r.text());return;}
    const j=await r.json();jobId=j.id;fullHtml=j.html;sections=j.sections||[];replay='';loadRuns();
    buildTabs();$('dl').style.display='block';$('xl').style.display=j.xlsx?'block':'none';
    $('status').textContent='Done — '+j.files+' section(s). '+(sections.length?'Tabs: '+sections.map(x=>x.title).join(', ')+', and the Full Document.':'Scroll to read, or download as Word.')
      +(j.docx_warning?'\\n\\n⚠ The Word file uses the PLAIN format, not the formatted one. Reason: '+j.docx_warning:'');
  }catch(e){$('status').textContent='Failed: '+e;}finally{$('go').disabled=false;}
};
$('dl').onclick=()=>{if(jobId)window.location='/download/'+jobId;};
$('xl').onclick=()=>{if(jobId)window.location='/download_xlsx/'+jobId;};
async function loadRuns(){
  try{const r=await fetch('/runs');const list=await r.json();
    $('runs').innerHTML=list.length?list.map(m=>'<option value="'+m.id+'">'+m.when+' · '+m.backend+' · '+m.source+'</option>').join(''):'<option value="">— none yet —</option>';
  }catch(e){}
}
$('load').onclick=async()=>{
  const id=$('runs').value;if(!id){$('status').textContent='No saved run selected.';return;}
  $('status').textContent='Loading saved run…';
  try{const r=await fetch('/runs/'+encodeURIComponent(id));
    if(!r.ok){$('status').textContent='Error: '+(await r.text());return;}
    const j=await r.json();jobId=j.id||null;fullHtml=j.html;sections=j.sections||[];
    const m=j.meta||{};replay='Saved run &middot; produced by the <b>'+m.backend+'</b> backend on '+m.when+' from '+m.source+' &middot; reloaded, not re-run';
    buildTabs();$('dl').style.display=jobId?'block':'none';$('xl').style.display=j.xlsx?'block':'none';
    $('status').textContent='Loaded saved run from '+m.when+' ('+m.backend+').';
  }catch(e){$('status').textContent='Failed: '+e;}
};
loadRuns();
</script></body></html>"""


# ── endpoints ────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.post("/analyze/preview")
async def analyze_preview(
    file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = Form(None),
    backend: str = Form("heuristic"),
    target: Optional[str] = Form(None),
    title: str = Form("Operational Specification"),
    standards: Optional[UploadFile] = File(None),
):
    """Run reversa, return the spec as HTML for the browser plus a job id for the docx."""
    if not file and not repo_url:
        raise HTTPException(400, "Provide either a zip file or repo_url")
    _check_backend(backend)
    work = Path(tempfile.mkdtemp(prefix="reversa_"))
    data = await file.read() if file else None
    std_path = None
    if standards is not None and standards.filename:
        raw = await standards.read()
        try:
            parsed = json.loads(raw)
            assert isinstance(parsed.get("rules"), list)
        except Exception:
            raise HTTPException(400, "Standards file must be JSON with a 'rules' list")
        std_path = work / "standards.json"
        std_path.write_bytes(raw)
    sdd = _obtain_and_run(work, data, repo_url, backend, target, std_path)
    md = _collect_markdown(sdd, title)
    out = work / "reversa_spec.docx"
    docx_warning = _to_docx(sdd, md, out, title)
    job = uuid.uuid4().hex
    RESULTS[job] = out
    xl = sdd / "comparison.xlsx"
    if xl.exists():
        keep = Path(tempfile.mkdtemp(prefix="reversa_xlsx_")) / "standards_comparison.xlsx"
        shutil.copy(xl, keep)                 # separate folder: the docx download deletes `work`
        XLSX[job] = keep
    n_files = len(list(sdd.rglob("*.md")))
    sections = _panel_sections(sdd)
    overview = _llm_business_context(md, title, backend)
    if overview:
        # Synthesized plain-English overview leads; rules, gaps and the layered
        # ops spec follow as their own tabs.
        sections = [{"title": "Business Context",
                     "file": "synthesized from the extracted specification",
                     "html": pypandoc.convert_text(overview, "html", format="gfm")}] + sections
    payload = {"id": job, "files": n_files, "html": _to_html(md), "sections": sections,
               "docx_warning": docx_warning,
               "xlsx": job in XLSX}
    _save_run(payload, out, backend, title, (file.filename if file else repo_url) or "run", XLSX.get(job))
    return JSONResponse(payload)


@app.get("/runs")
def list_runs():
    """Saved analyses, newest first."""
    runs = []
    if RUNS_DIR.exists():
        for d in sorted(RUNS_DIR.iterdir(), reverse=True):
            f = d / "run.json"
            if f.exists():
                try:
                    runs.append(json.loads(f.read_text(encoding="utf-8"))["meta"])
                except Exception:
                    continue
    return JSONResponse(runs)


@app.get("/runs/{rid}")
def load_run(rid: str):
    """Reload a saved analysis into the tabs (and make its Word document downloadable)."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", rid):
        raise HTTPException(400, "bad run id")
    f = RUNS_DIR / rid / "run.json"
    if not f.exists():
        raise HTTPException(404, "saved run not found")
    data = json.loads(f.read_text(encoding="utf-8"))
    saved_docx = RUNS_DIR / rid / "reversa_spec.docx"
    if saved_docx.exists():
        tmp = Path(tempfile.mkdtemp(prefix="reversa_replay_"))
        shutil.copy(saved_docx, tmp / "reversa_spec.docx")   # download deletes its copy, not the saved one
        job = uuid.uuid4().hex
        RESULTS[job] = tmp / "reversa_spec.docx"
        data["id"] = job
        saved_xl = RUNS_DIR / rid / "standards_comparison.xlsx"
        if saved_xl.exists():
            XLSX[job] = saved_xl
        data["xlsx"] = job in XLSX
    return JSONResponse(data)


@app.get("/download_xlsx/{job}")
def download_xlsx(job: str):
    """The Standards Comparison tab as an Excel workbook (Summary, Comparison, Additional in code)."""
    path = XLSX.get(job)
    if not path or not path.exists():
        raise HTTPException(404, "No standards comparison for this run")
    return FileResponse(path, filename="standards_comparison.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/download/{job}")
def download(job: str, background: BackgroundTasks):
    path = RESULTS.pop(job, None)
    if not path or not path.exists():
        raise HTTPException(404, "Result expired — run the analysis again")
    background.add_task(shutil.rmtree, path.parent, ignore_errors=True)
    return FileResponse(path, filename="reversa_spec.docx",
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.get("/health")
def health():
    ok = shutil.which("git") is not None
    return {"status": "ok", "git": ok, "pandoc": pypandoc.get_pandoc_version(),
            "docx_export": DOCX_EXPORT_STATUS, "python": sys.executable}


@app.post("/analyze")
async def analyze(
    background: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = Form(None),
    backend: str = Form("heuristic"),
    target: Optional[str] = Form(None),
    title: str = Form("Operational Specification"),
):
    if not file and not repo_url:
        raise HTTPException(400, "Provide either a zip file or repo_url")
    _check_backend(backend)

    work = Path(tempfile.mkdtemp(prefix="reversa_"))
    background.add_task(shutil.rmtree, work, ignore_errors=True)   # cleanup after response
    src = work / "src"
    src.mkdir()

    # 1. obtain the codebase
    if file:
        zip_path = work / "upload.zip"
        data = await file.read()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(413, f"Upload exceeds {MAX_UPLOAD_MB} MB")
        zip_path.write_bytes(data)
        _safe_extract(zip_path, src)
    else:
        if not re.match(r"^https?://", repo_url or ""):
            raise HTTPException(400, "repo_url must be an http(s) git URL")
        _run(["git", "clone", "--depth", "1", repo_url, str(src)], cwd=work, env=os.environ.copy())

    project = _project_root(src)

    # 2. run reversa (install → run) using the same interpreter that serves the API
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    std = DEFAULT_STANDARDS if DEFAULT_STANDARDS.exists() else None   # was an undefined `standards`
    if std:
        env["REVERSA_STANDARDS"] = str(std)
    py = [sys.executable, "-m", "reversa"]
    _run(py + ["install"], cwd=project, env=env)
    run_cmd = py + ["run", "--backend", backend]
    if target:
        run_cmd += ["--target", target]
    _run(run_cmd, cwd=project, env=env)

    # 3. markdown → docx
    sdd = project / SDD_DIR
    md = _collect_markdown(sdd, title)
    out = work / "reversa_spec.docx"
    docx_warning = _to_docx(sdd, md, out, title)

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_") or "reversa_spec"
    return FileResponse(out, filename=f"{safe}.docx",
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"X-Reversa-Docx-Warning": docx_warning[:500]} if docx_warning else None)
