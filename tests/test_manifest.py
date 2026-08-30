from pathlib import Path

from reversa import installer
from reversa.manifest import Manifest


def _quiet(*_a, **_k):
    pass


def test_install_status_update_uninstall_preserve(atm: Path):
    installer.install(atm, ["claude", "codex"], log=_quiet)
    assert (atm / "CLAUDE.md").exists() and (atm / "AGENTS.md").exists()
    assert (atm / ".claude/skills/reversa-reviewer/SKILL.md").exists()
    assert all(f.status == "intact" for f in installer.status(atm))

    # user edits the entry file
    claude = atm / "CLAUDE.md"
    claude.write_text(claude.read_text() + "\n# my local notes\n")
    st = {f.path: f.status for f in installer.status(atm)}
    assert st["CLAUDE.md"] == "modified"

    # user deletes a skill
    (atm / ".codex/skills/reversa-scout/SKILL.md").unlink()
    st = {f.path: f.status for f in installer.status(atm)}
    assert st[".codex/skills/reversa-scout/SKILL.md"] == "missing"

    # update: modified preserved, missing re-created
    acts = installer.update(atm, log=_quiet)
    assert "CLAUDE.md" in acts["preserved"]
    assert (atm / ".codex/skills/reversa-scout/SKILL.md").exists()
    assert "# my local notes" in claude.read_text()

    # uninstall: modified file survives, intact files go
    out = installer.uninstall(atm, log=_quiet)
    assert "CLAUDE.md" in out["preserved"] and claude.exists()
    assert not (atm / "AGENTS.md").exists()
    assert not (atm / ".claude/skills").exists()
    # legacy sources untouched
    assert (atm / "CONTA.cbl").exists()


def test_uninstall_purge_removes_modified(atm: Path):
    installer.install(atm, ["claude"], log=_quiet)
    (atm / "CLAUDE.md").write_text("changed")
    installer.uninstall(atm, purge=True, log=_quiet)
    assert not (atm / "CLAUDE.md").exists()
    assert not (atm / ".reversa").exists()


def test_add_engine(atm: Path):
    installer.install(atm, ["claude"], log=_quiet)
    installer.add_engine(atm, "gemini", log=_quiet)
    assert (atm / "GEMINI.md").exists()
    m = Manifest(atm).load()
    assert "GEMINI.md" in m.entries
