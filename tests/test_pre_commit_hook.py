"""The pre-commit hook's `files` pattern: every file that changes wheelgap's answer must trigger a run
(#486), without matching files that don't."""

import re
from pathlib import Path

import pytest

FILES_LINE = re.compile(r"^  files: (\S+)$", re.MULTILINE)
PATTERN = re.compile(
    FILES_LINE.search((Path(__file__).parent.parent / ".pre-commit-hooks.yaml").read_text()).group(1)  # type: ignore[union-attr]
)


@pytest.mark.parametrize(
    "name",
    [
        "uv.lock",
        "poetry.lock",
        "pdm.lock",
        "pylock.toml",
        "Pipfile.lock",
        "pixi.lock",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements.lock",
        "pyproject.toml",
        "sub/pyproject.toml",
        "uv.toml",
        "sub/uv.toml",
        ".python-version",
        "sub/.python-version",
    ],
)
def test_hook_files_pattern_matches(name):
    assert PATTERN.search(name), name


@pytest.mark.parametrize("name", ["README.md", "setup.py", "setup.cfg", "sub/requirements.in", "tox.ini"])
def test_hook_files_pattern_doesnt_match(name):
    assert not PATTERN.search(name), name
