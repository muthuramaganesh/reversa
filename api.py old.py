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
from fastapi.responses import FileResponse

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


# ── endpoints ────────────────────────────────────────────────────────────────
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
