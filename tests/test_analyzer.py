"""Unit tests for RepoAnalyzer."""

from pathlib import Path

import pytest

from gitpulse.analyzer import (
    EmptyRepositoryError,
    NotAGitRepositoryError,
    RepoAnalyzer,
)


def test_non_existent_directory(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist"
    with pytest.raises(NotAGitRepositoryError):
        RepoAnalyzer(non_existent)


def test_non_git_directory(tmp_path: Path) -> None:
    regular_dir = tmp_path / "regular_dir"
    regular_dir.mkdir()
    with pytest.raises(NotAGitRepositoryError):
        RepoAnalyzer(regular_dir)


def test_empty_git_repository(empty_git_repo: Path) -> None:
    analyzer = RepoAnalyzer(empty_git_repo)
    with pytest.raises(EmptyRepositoryError):
        analyzer.summary()


def test_populated_git_repo_analysis(populated_git_repo: Path) -> None:
    analyzer = RepoAnalyzer(populated_git_repo)

    assert analyzer.get_current_branch() == "main"
    assert analyzer.get_repo_name() == "test_repo"

    files = analyzer.get_tracked_files()
    assert "main.py" in files
    assert "README.md" in files

    file_types = analyzer.get_file_type_breakdown()
    exts = [ft.extension for ft in file_types]
    assert ".py" in exts
    assert ".md" in exts

    commits = analyzer.get_commits()
    assert len(commits) == 3

    contributors = analyzer.get_contributors()
    assert len(contributors) == 2
    # Alice has 2 commits, Bob has 1 commit
    assert contributors[0].name == "Alice Dev"
    assert contributors[0].commits == 2
    assert contributors[1].name == "Bob Builder"
    assert contributors[1].commits == 1

    summary = analyzer.summary()
    assert summary.total_commits == 3
    assert summary.total_contributors == 2
    assert summary.total_files == 2
    assert summary.first_commit_date is not None
    assert summary.latest_commit_date is not None


def test_to_json(populated_git_repo: Path) -> None:
    analyzer = RepoAnalyzer(populated_git_repo)
    json_str = analyzer.to_json()
    assert '"total_commits": 3' in json_str
    assert '"repo_name": "test_repo"' in json_str
