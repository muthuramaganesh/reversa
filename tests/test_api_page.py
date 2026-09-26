"""The single-page UI in api.py must ship valid JavaScript.

A syntax error anywhere in the <script> silently disables the whole page (Analyse does
nothing, saved runs never load). Python escapes in INDEX_HTML are the usual culprit:
"\\n" in the Python source becomes a raw newline inside a JS string literal.
"""
import re
import shutil
import subprocess

import pytest

api = pytest.importorskip("api")


def _script() -> str:
    return re.search(r"<script>(.*)</script>", api.INDEX_HTML, re.S).group(1)


def test_no_raw_newline_inside_js_string():
    for n, line in enumerate(_script().splitlines(), 1):
        code = re.sub(r"\\.", "", line)                  # drop escaped chars (\' \\ \n ...)
        assert code.count("'") % 2 == 0, f"unterminated '...' string on script line {n}: {line.strip()[:80]}"


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_script_parses(tmp_path):
    js = tmp_path / "page.js"
    js.write_text(_script(), encoding="utf-8")
    proc = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
