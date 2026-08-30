import shutil
from pathlib import Path

import pytest

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "legacy_atm"


@pytest.fixture
def atm(tmp_path: Path) -> Path:
    dst = tmp_path / "atm"
    shutil.copytree(EXAMPLE, dst)
    return dst
