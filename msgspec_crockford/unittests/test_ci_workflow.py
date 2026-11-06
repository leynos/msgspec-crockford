"""Contract tests for the Rust tool cache in the CI workflow.

`install-whitaker` provisions its own installer and suite checkout. When the
rust-cache step also restored `~/.local/share/whitaker` from an older run, the
installer's `git pull` aborted in that stale checkout with "untracked working
tree files would be overwritten by merge". These tests keep the Whitaker paths
out of that cache and the cargo tool paths in it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "ci.yml"
CACHE_STEP = "Cache Rust lint and test tools"
CACHE_KEY = "without-whitaker"
CARGO_TOOLS = {"~/.cargo/bin/cargo-nextest", "~/.cargo/bin/cargo-audit"}
WHITAKER_PATH_RE = re.compile(r"whitaker", re.IGNORECASE)
_STEP_RE = re.compile(r"^( *)- name: (.+)$", re.MULTILINE)


def _step_text(workflow: str, name: str) -> str:
    """Return the text of the workflow step called *name*, or an empty string."""
    matches = list(_STEP_RE.finditer(workflow))
    for index, match in enumerate(matches):
        if match.group(2).strip() == name:
            following = matches[index + 1] if index + 1 < len(matches) else None
            end = following.start() if following else len(workflow)
            return workflow[match.start() : end]
    return ""


def cache_directories(workflow: str) -> list[str]:
    """Return the paths in the cache step's ``cache-directories`` block.

    Comment lines are skipped, so an explanation of why a path is absent does
    not count as a cached path.
    """
    step = _step_text(workflow, CACHE_STEP)
    block = re.search(r"cache-directories: \|\n((?:[ \t]+.*\n?)+)", step)
    if block is None:
        return []
    lines = (line.strip() for line in block.group(1).splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def test_the_cache_step_caches_exactly_the_cargo_tools() -> None:
    """The cache step lists the cargo tools and nothing else."""
    paths = cache_directories(CI_WORKFLOW.read_text("utf-8"))

    assert set(paths) == CARGO_TOOLS, paths


def test_the_cache_key_separates_it_from_archives_that_hold_whitaker() -> None:
    """The cache step carries its own key, so older archives are not restored.

    Those archives were saved with the Whitaker paths and still hold the stale
    checkout, which dropping the paths alone does not stop from being restored.
    """
    step = _step_text(CI_WORKFLOW.read_text("utf-8"), CACHE_STEP)

    assert re.search(rf"^\s+key: {CACHE_KEY}$", step, re.MULTILINE), step


def test_no_cached_path_is_a_whitaker_path() -> None:
    """No cached path may restore a Whitaker checkout, installer or wrapper."""
    paths = cache_directories(CI_WORKFLOW.read_text("utf-8"))

    assert paths, "the cache step must list the cargo tool paths"
    assert not [path for path in paths if WHITAKER_PATH_RE.search(path)], paths


@pytest.mark.parametrize(
    "path",
    [
        "~/.local/share/whitaker",
        "~/.local/bin/whitaker",
        "~/.cargo/bin/whitaker-installer",
    ],
)
def test_the_reader_reports_a_whitaker_path_when_one_is_cached(path: str) -> None:
    """A cached Whitaker path is reported, so the contract cannot pass vacuously."""
    workflow = (
        "steps:\n"
        f"  - name: {CACHE_STEP}\n"
        "    with:\n"
        "      cache-directories: |\n"
        "        # a comment is not a path\n"
        "        ~/.cargo/bin/cargo-nextest\n"
        f"        {path}\n"
        "  - name: Next step\n"
        "    run: true\n"
    )

    paths = cache_directories(workflow)

    assert paths == ["~/.cargo/bin/cargo-nextest", path]
    assert [p for p in paths if WHITAKER_PATH_RE.search(p)] == [path]


def test_a_missing_cache_step_yields_no_paths() -> None:
    """A workflow without the step reports no paths rather than raising."""
    assert cache_directories("steps:\n  - name: Other\n    run: true\n") == []
