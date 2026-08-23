"""Unit tests for gitpulse data models."""

from datetime import datetime, timezone

from gitpulse.models import ContributorStats, FileTypeStats, RepoSummary


def test_contributor_stats_to_dict() -> None:
    now = datetime.now(timezone.utc)
    stats = ContributorStats(
        name="Alice",
        email="alice@example.com",
        commits=10,
        insertions=150,
        deletions=25,
        first_commit=now,
        last_commit=now,
        percentage_of_commits=50.0,
    )
    d = stats.to_dict()
    assert d["name"] == "Alice"
    assert d["email"] == "alice@example.com"
    assert d["commits"] == 10
    assert d["percentage_of_commits"] == 50.0


def test_file_type_stats_to_dict() -> None:
    stats = FileTypeStats(extension=".py", count=15, percentage=75.5)
    d = stats.to_dict()
    assert d["extension"] == ".py"
    assert d["count"] == 15
    assert d["percentage"] == 75.5


def test_repo_summary_to_dict() -> None:
    now = datetime.now(timezone.utc)
    summary = RepoSummary(
        repo_name="my-repo",
        repo_path="/path/to/my-repo",
        current_branch="main",
        total_commits=1,
        total_contributors=1,
        total_files=2,
        total_insertions=10,
        total_deletions=2,
        first_commit_date=now,
        latest_commit_date=now,
    )
    d = summary.to_dict()
    assert d["repo_name"] == "my-repo"
    assert d["total_commits"] == 1
    assert isinstance(d["first_commit_date"], str)
