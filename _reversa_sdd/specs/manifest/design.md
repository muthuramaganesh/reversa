# Design — MANIFEST

## Structure
MANIFEST is organised into 10 functions: sha256_of, FileStatus, Manifest, __init__, load, save, record, record_many, classify, status_of.

## Data
MANIFEST performs sha256_of on open.

## Dependencies
MANIFEST depends on __FUTURE__ (import). MANIFEST depends on HASHLIB (import). MANIFEST depends on JSON (import). MANIFEST depends on DATACLASSES (import). MANIFEST depends on PATHLIB (import). MANIFEST depends on TYPING (import).

_Derived from claims: C-045, C-046, C-047, C-048, C-049, C-050, C-214, C-215_
