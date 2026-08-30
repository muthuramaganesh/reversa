"""SHA-256 file manifest (paper §3.3).

Every file Reversa installs into a project is recorded with its hash in
`.reversa/_config/files-manifest.json`. On `status`, `update` and `uninstall`
each file is classified as:

    intact    hash matches -> safe to overwrite / delete
    modified  hash differs -> user edited it -> preserve
    missing   file gone    -> may be re-created on update, ignored on uninstall
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MANIFEST_REL = Path(".reversa/_config/files-manifest.json")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class FileStatus:
    path: str
    status: str  # intact | modified | missing
    expected: str
    actual: str | None


class Manifest:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / MANIFEST_REL
        self.entries: dict[str, str] = {}
        self.version: str = ""

    def load(self) -> "Manifest":
        if self.path.exists():
            d = json.loads(self.path.read_text(encoding="utf-8"))
            self.entries = d.get("files", {})
            self.version = d.get("version", "")
        return self

    def save(self, version: str) -> None:
        self.version = version
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"version": version, "algorithm": "sha256",
                        "files": dict(sorted(self.entries.items()))}, indent=2),
            encoding="utf-8",
        )

    def record(self, rel: str) -> None:
        self.entries[rel] = sha256_of(self.root / rel)

    def record_many(self, rels: Iterable[str]) -> None:
        for r in rels:
            self.record(r)

    def classify(self) -> list[FileStatus]:
        out: list[FileStatus] = []
        for rel, expected in sorted(self.entries.items()):
            p = self.root / rel
            if not p.exists():
                out.append(FileStatus(rel, "missing", expected, None))
                continue
            actual = sha256_of(p)
            out.append(FileStatus(rel, "intact" if actual == expected else "modified",
                                  expected, actual))
        return out

    def status_of(self, rel: str) -> str:
        for fs in self.classify():
            if fs.path == rel:
                return fs.status
        return "untracked"
