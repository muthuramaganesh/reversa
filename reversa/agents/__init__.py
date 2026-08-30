"""Reversa agent teams (paper §3.4).

Discovery team (in execution order): scout -> archaeologist -> detective ->
architect -> writer -> reviewer. Migration team: migration.
"""
from .scout import Scout
from .archaeologist import Archaeologist
from .detective import Detective
from .architect import Architect
from .process import ProcessAgent
from .writer import Writer
from .reviewer import Reviewer
from .migration import Migration

DISCOVERY = [Scout, Archaeologist, Detective, Architect, ProcessAgent, Writer, Reviewer]
MIGRATION = [Migration]
ALL = {a.name: a for a in DISCOVERY + MIGRATION}

__all__ = ["Scout", "Archaeologist", "Detective", "Architect", "ProcessAgent", "Writer", "Reviewer",
           "Migration", "DISCOVERY", "MIGRATION", "ALL"]
