# Reversa API — deploy notes

## Files to add to ~/Documents/reversa
- `api.py`            (this file, at the repo root next to pyproject.toml)
- `requirements.txt`  (API deps; reversa itself is installed from pyproject via `pip install .`)
- `runtime.txt`       containing `python-3.12.9`

## Local test
    cd ~/Documents/reversa
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt && pip install -e .
    uvicorn api:app --reload --port 8000

    # in another terminal — analyse a zipped project and save the Word doc
    curl -s -X POST http://localhost:8000/analyze \
      -F "file=@/path/to/legacy-project.zip" \
      -F "backend=heuristic" -F "title=Legacy Payments Spec" \
      -o spec.docx && open spec.docx

    # or from a public git repo
    curl -s -X POST http://localhost:8000/analyze \
      -F "repo_url=https://github.com/someone/legacy-app" -o spec.docx

## Render
- New Web Service → repo `reversa` → Region Singapore → Runtime Python 3
- Build:  `pip install -r requirements.txt && pip install .`
- Start:  `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Instance: Starter (heuristic backend) — Standard if you enable the Anthropic backend
- Env vars: `ANTHROPIC_API_KEY` (only if you want backend=anthropic), optionally
  `RUN_TIMEOUT_S=900`, `MAX_UPLOAD_MB=50`
- Render's HTTP timeout is 100 s on Starter; long analyses on large repos may need the
  heuristic backend or a paid plan with longer timeouts.

## .gitignore additions
    venv/
    __pycache__/
    .pytest_cache/
    *.egg-info/
    .DS_Store
