"""Access to the legacy project on disk.

The legacy system is the primary source of evidence (paper §3.2). This module
inventories it and gives agents a safe way to read files and cite line ranges.
"""
from __future__ import annotations

import os
from pathlib import Path

from .models import SourceFile

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", "target", ".reversa", "_reversa_sdd", ".idea", ".vscode",
    ".claude", ".codex", ".cursor", ".gemini",
}

LANGUAGES: dict[str, str] = {
    ".cbl": "cobol", ".cob": "cobol", ".cpy": "cobol-copybook", ".jcl": "jcl",
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".jsx": "javascript",
    ".tsx": "typescript", ".java": "java", ".go": "go", ".rb": "ruby", ".php": "php",
    ".cs": "csharp", ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".rs": "rust",
    ".kt": "kotlin", ".swift": "swift", ".pl": "perl", ".sh": "shell", ".bas": "basic",
    ".vb": "vb", ".pas": "pascal", ".sql": "sql", ".prg": "clipper", ".rpg": "rpg",
    ".rpgle": "rpg", ".abap": "abap", ".sas": "sas", ".r": "r", ".scala": "scala",
    ".xml": "xml", ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".ini": "ini", ".cfg": "ini", ".properties": "properties", ".md": "markdown",
    ".txt": "text", ".csv": "data", ".dat": "data", ".html": "html", ".css": "css",
}

CODE_LANGS = {
    "cobol", "cobol-copybook", "python", "javascript", "typescript", "java", "go",
    "ruby", "php", "csharp", "c", "cpp", "rust", "kotlin", "swift", "perl", "shell",
    "basic", "vb", "pascal", "sql", "clipper", "rpg", "abap", "sas", "r", "scala", "jcl",
}

MAX_FILE_BYTES = 400_000


class Project:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._cache: dict[str, list[str]] = {}

    def inventory(self) -> list[SourceFile]:
        files: list[SourceFile] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS
                                 and not d.startswith(".git"))
            for fn in sorted(filenames):
                p = Path(dirpath) / fn
                rel = p.relative_to(self.root).as_posix()
                ext = p.suffix.lower()
                lang = LANGUAGES.get(ext)
                if lang is None:
                    continue
                try:
                    size = p.stat().st_size
                except OSError:
                    continue
                if size > MAX_FILE_BYTES:
                    continue
                files.append(SourceFile(path=rel, language=lang,
                                        lines=len(self.lines(rel)), size=size))
        return files

    def lines(self, rel: str) -> list[str]:
        if rel not in self._cache:
            p = self.root / rel
            try:
                self._cache[rel] = p.read_text(encoding="utf-8",
                                               errors="replace").splitlines()
            except OSError:
                self._cache[rel] = []
        return self._cache[rel]

    def text(self, rel: str) -> str:
        return "\n".join(self.lines(rel))

    def numbered(self, rel: str, max_lines: int | None = None) -> str:
        ls = self.lines(rel)
        if max_lines:
            ls = ls[:max_lines]
        return "\n".join(f"{i + 1:5d}| {l}" for i, l in enumerate(ls))

    def code_files(self, inv: list[SourceFile]) -> list[SourceFile]:
        return [f for f in inv if f.language in CODE_LANGS]
