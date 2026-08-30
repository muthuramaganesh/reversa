"""Reversa: reverse documentation engineering for legacy systems.

Implements the framework described in:
  Macedo, S. O. & Costa, R. M. (2026). Reversa: A Reverse Documentation
  Engineering Framework for Converting Legacy Software into Operational
  Specifications for AI Agents. arXiv:2605.18684.

Core ideas implemented here:
  * a multi-agent Discovery pipeline (scout -> archaeologist -> detective ->
    architect -> writer -> reviewer) plus a Migration team (parity scenarios);
  * a confidence model in which every claim is CONFIRMED, INFERRED or a GAP,
    with an internal confidence index (confirmed=1.0, inferred=0.5, gap=0);
  * traceability from every claim back to file/line evidence;
  * an artifact layer under _reversa_sdd/ and operational state under .reversa/;
  * a SHA-256 files manifest that classifies installed files as intact,
    modified or missing so update/uninstall never destroy user edits.
"""
__version__ = "0.1.0"
