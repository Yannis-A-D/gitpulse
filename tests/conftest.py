"""Pytest fixtures for creating mock Git repositories."""

from __future__ import annotations

import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest


def run_git_cmd(repo_path: Path, args: list[str]) -> None:
    """Helper to run git commands during fixture setup."""
    subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def empty_git_repo(tmp_path: Path) -> Path:
    """Fixture that initializes a bare empty git repo with no commits."""
    repo = tmp_path / "empty_repo"
    repo.mkdir()
    run_git_cmd(repo, ["init"])
    run_git_cmd(repo, ["config", "user.name", "Test User"])
    run_git_cmd(repo, ["config", "user.email", "test@example.com"])
    return repo


@pytest.fixture
def populated_git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture creating a temporary git repo with multiple commits, authors, and files."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    run_git_cmd(repo, ["init", "-b", "main"])
    run_git_cmd(repo, ["config", "user.name", "Alice Dev"])
    run_git_cmd(repo, ["config", "user.email", "alice@example.com"])

    # Commit 1 by Alice
    file1 = repo / "main.py"
    file1.write_text("print('hello world')\n", encoding="utf-8")
    run_git_cmd(repo, ["add", "main.py"])
    run_git_cmd(repo, ["commit", "-m", "Initial commit"])

    # Commit 2 by Bob
    run_git_cmd(repo, ["config", "user.name", "Bob Builder"])
    run_git_cmd(repo, ["config", "user.email", "bob@example.com"])
    file2 = repo / "README.md"
    file2.write_text("# Project\n\nDocs here.\n", encoding="utf-8")
    run_git_cmd(repo, ["add", "README.md"])
    run_git_cmd(repo, ["commit", "-m", "Add README"])

    # Commit 3 by Alice (Modifying main.py)
    run_git_cmd(repo, ["config", "user.name", "Alice Dev"])
    run_git_cmd(repo, ["config", "user.email", "alice@example.com"])
    file1.write_text("print('hello world')\nprint('welcome')\n", encoding="utf-8")
    run_git_cmd(repo, ["add", "main.py"])
    run_git_cmd(repo, ["commit", "-m", "Update greeting"])

    yield repo
