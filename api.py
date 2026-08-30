"""
Reversa API — run reverse-documentation on a codebase and return a Word document.

POST /analyze            multipart: file=<zip>  OR  repo_url=<git url>
                         optional form fields: backend (heuristic|anthropic), target (e.g. go), title
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

app = FastAPI(title="Reversa API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
RUN_TIMEOUT_S = int(os.getenv("RUN_TIMEOUT_S", "900"))          # 15 min ceiling for reversa run
SDD_DIR = "_reversa_sdd"
# Preferred reading order for the Word doc; anything else follows alphabetically.
ORDER = ["README.md", "inventory.md", "rules.md", "architecture.md", "process.md",
         "migration.md", "risks.md", "gaps.md", "questions.md"]


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
    files = sorted(sdd.rglob("*.md"),
                   key=lambda p: (ORDER.index(p.name) if p.name in ORDER else len(ORDER),
                                  str(p.relative_to(sdd))))
    if not files:
        raise HTTPException(500, f"reversa produced no Markdown under {SDD_DIR}")

    parts = [f"% {title}\n"]                     # pandoc title block → Word title
    for f in files:
        section = f.relative_to(sdd).with_suffix("").as_posix().replace("/", " › ")
        body = f.read_text(encoding="utf-8", errors="replace")
        body = re.sub(r"^(#{1,5})\s", lambda m: "#" * (len(m.group(1)) + 1) + " ", body, flags=re.M)
        parts.append(f"\n\n# {section}\n\n{body}")
    return "\n".join(parts)


def _to_docx(markdown: str, out: Path) -> None:
    pypandoc.convert_text(
        markdown, "docx", format="gfm",
        outputfile=str(out),
        extra_args=["--toc", "--toc-depth=2", "--standalone"],
    )


def _to_html(markdown: str) -> str:
    return pypandoc.convert_text(markdown, "html", format="gfm",
                                 extra_args=["--toc", "--toc-depth=2"])


RESULTS: dict[str, Path] = {}          # job id → docx path (ephemeral; fine for a demo)

# Docs surfaced in the side panel for business readers: (tab title, candidate files
# in priority order — first match under _reversa_sdd wins).
PANEL_FILES = [
    ("Business Context", ["business_context.md", "context.md", "rules.md", "README.md"]),
    ("Process", ["process.md"]),
]


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


def _obtain_and_run(work: Path, file_bytes: Optional[bytes], repo_url: Optional[str],
                    backend: str, target: Optional[str]) -> Path:
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
</style></head><body>
<header><h1>Reversa</h1><span>Reverse documentation engineering — upload a legacy codebase, get a traceable operational specification</span></header>
<main>
<aside>
 <label>Codebase (zip)</label><input type="file" id="file" accept=".zip">
 <label>…or public git URL</label><input type="text" id="repo" placeholder="https://github.com/org/legacy-app">
 <label>Backend</label><select id="backend"><option value="heuristic">heuristic (offline, fast)</option><option value="anthropic">anthropic (LLM agents)</option></select>
 <label>Migration target (optional)</label><input type="text" id="target" placeholder="e.g. go, java, python">
 <label>Document title</label><input type="text" id="title" value="Operational Specification">
 <button id="go">Analyse</button>
 <button id="dl">Download Word document</button>
 <div id="status"></div>
</aside>
<section><div id="out"><p class="empty">The specification will appear here.</p></div></section>
</main>
<script>
const $=id=>document.getElementById(id);let jobId=null;let fullHtml='';let sections=[];let tabs=[];let active=0;
function _top(){const s=document.querySelector('section');if(s)s.scrollTop=0;}
function buildTabs(){
  tabs=sections.concat([{title:'Detailed Ops Spec',file:'',html:fullHtml}]);
  active=0;renderTab();
}
function renderTab(){
  const bar='<div class="tabbar">'+tabs.map((t,i)=>'<button class="'+(i===active?'active':'')+'" onclick="setTab('+i+')">'+t.title+'</button>').join('')+'</div>';
  const t=tabs[active];
  const src=t.file?'<div class="srcnote">source: '+t.file+' &middot; extracted from the code by Reversa</div>':'';
  $('out').innerHTML=bar+src+t.html;_top();
}
function setTab(i){active=i;renderTab();}
$('go').onclick=async()=>{
  const fd=new FormData();const f=$('file').files[0];
  if(f)fd.append('file',f);else if($('repo').value.trim())fd.append('repo_url',$('repo').value.trim());
  else{ $('status').textContent='Choose a zip or enter a git URL.';return; }
  fd.append('backend',$('backend').value);fd.append('title',$('title').value||'Operational Specification');
  if($('target').value.trim())fd.append('target',$('target').value.trim());
  $('go').disabled=true;$('dl').style.display='none';$('status').textContent='Running reversa… this can take up to a minute.';
  try{
    const r=await fetch('/analyze/preview',{method:'POST',body:fd});
    if(!r.ok){$('status').textContent='Error: '+(await r.text());return;}
    const j=await r.json();jobId=j.id;fullHtml=j.html;sections=j.sections||[];
    buildTabs();$('dl').style.display='block';
    $('status').textContent='Done — '+j.files+' section(s). '+(sections.length?'Tabs: Business Context, Process, and the full Detailed Ops Spec.':'Scroll to read, or download as Word.');
  }catch(e){$('status').textContent='Failed: '+e;}finally{$('go').disabled=false;}
};
$('dl').onclick=()=>{if(jobId)window.location='/download/'+jobId;};
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
):
    """Run reversa, return the spec as HTML for the browser plus a job id for the docx."""
    if not file and not repo_url:
        raise HTTPException(400, "Provide either a zip file or repo_url")
    if backend not in ("heuristic", "anthropic"):
        raise HTTPException(400, "backend must be 'heuristic' or 'anthropic'")
    if backend == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(400, "ANTHROPIC_API_KEY is not set on the server; use backend=heuristic")
    work = Path(tempfile.mkdtemp(prefix="reversa_"))
    data = await file.read() if file else None
    sdd = _obtain_and_run(work, data, repo_url, backend, target)
    md = _collect_markdown(sdd, title)
    out = work / "reversa_spec.docx"
    _to_docx(md, out)
    job = uuid.uuid4().hex
    RESULTS[job] = out
    n_files = len(list(sdd.rglob("*.md")))
    return JSONResponse({"id": job, "files": n_files, "html": _to_html(md),
                         "sections": _panel_sections(sdd)})


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
    return {"status": "ok", "git": ok, "pandoc": pypandoc.get_pandoc_version()}


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
    if backend not in ("heuristic", "anthropic"):
        raise HTTPException(400, "backend must be 'heuristic' or 'anthropic'")
    if backend == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(400, "ANTHROPIC_API_KEY is not set on the server; use backend=heuristic")

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
    _to_docx(md, out)

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_") or "reversa_spec"
    return FileResponse(out, filename=f"{safe}.docx",
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
