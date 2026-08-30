"""Coding-agent engine detection and entry-file installation (paper §3.3).

Reversa is portable across engines: for each selected engine it installs the
agent skills in the directory that engine expects and an entry file such as
CLAUDE.md, AGENTS.md or GEMINI.md that tells the engine how to run the
Reversa pipeline. Detection is heuristic, based on files/dirs commonly present
when an engine is in use.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Engine:
    key: str
    name: str
    entry_file: str                      # file the engine reads on startup
    skills_dir: str                      # where per-agent SKILL.md files go
    markers: tuple[str, ...] = field(default_factory=tuple)  # detection hints


ENGINES: dict[str, Engine] = {
    "claude": Engine("claude", "Claude Code", "CLAUDE.md", ".claude/skills",
                     (".claude", "CLAUDE.md")),
    "codex": Engine("codex", "Codex", "AGENTS.md", ".codex/skills",
                    (".codex", "AGENTS.md")),
    "cursor": Engine("cursor", "Cursor", ".cursor/rules/reversa.mdc", ".cursor/skills",
                     (".cursor",)),
    "gemini": Engine("gemini", "Gemini CLI", "GEMINI.md", ".gemini/skills",
                     (".gemini", "GEMINI.md")),
    "windsurf": Engine("windsurf", "Windsurf", ".windsurfrules", ".windsurf/skills",
                       (".windsurf", ".windsurfrules")),
    "kiro": Engine("kiro", "Kiro", ".kiro/steering/reversa.md", ".kiro/skills",
                   (".kiro",)),
    "opencode": Engine("opencode", "Opencode", "AGENTS.md", ".opencode/skills",
                       (".opencode",)),
    "cline": Engine("cline", "Cline", ".clinerules/reversa.md", ".cline/skills",
                    (".clinerules",)),
    "roo": Engine("roo", "Roo Code", ".roo/rules/reversa.md", ".roo/skills",
                  (".roo",)),
    "copilot": Engine("copilot", "GitHub Copilot", ".github/copilot-instructions.md",
                      ".github/skills", (".github/copilot-instructions.md",)),
    "aider": Engine("aider", "Aider", "CONVENTIONS.md", ".aider/skills",
                    (".aider.conf.yml", ".aider")),
    "amazonq": Engine("amazonq", "Amazon Q Developer", ".amazonq/rules/reversa.md",
                      ".amazonq/skills", (".amazonq",)),
    "antigravity": Engine("antigravity", "Antigravity", "AGENTS.md",
                          ".antigravity/skills", (".antigravity",)),
}


def detect_engines(root: Path) -> list[Engine]:
    found = []
    for e in ENGINES.values():
        if any((root / m).exists() for m in e.markers):
            found.append(e)
    return found


def resolve_engines(keys: list[str] | None, root: Path) -> list[Engine]:
    """Resolve CLI-supplied keys; fall back to detection; fall back to Claude+Codex."""
    if keys:
        unknown = [k for k in keys if k not in ENGINES]
        if unknown:
            raise ValueError(f"unknown engine(s): {', '.join(unknown)}; "
                             f"known: {', '.join(ENGINES)}")
        return [ENGINES[k] for k in keys]
    detected = detect_engines(root)
    return detected or [ENGINES["claude"], ENGINES["codex"]]
