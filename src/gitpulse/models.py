"""Data models representing Git statistics and repository metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CommitInfo:
    """Represents metadata of a single Git commit."""

    hash: str
    author_name: str
    author_email: str
    timestamp: datetime
    message: str
    insertions: int = 0
    deletions: int = 0
    files_changed: int = 0


@dataclass
class ContributorStats:
    """Aggregated statistics for a contributor."""

    name: str
    email: str
    commits: int
    insertions: int
    deletions: int
    first_commit: datetime
    last_commit: datetime
    percentage_of_commits: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to a serializable dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "commits": self.commits,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "first_commit": self.first_commit.isoformat(),
            "last_commit": self.last_commit.isoformat(),
            "percentage_of_commits": round(self.percentage_of_commits, 2),
        }


@dataclass
class FileTypeStats:
    """Statistics for files of a specific extension."""

    extension: str
    count: int
    percentage: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to a serializable dictionary."""
        return {
            "extension": self.extension,
            "count": self.count,
            "percentage": round(self.percentage, 2),
        }


@dataclass
class RepoSummary:
    """High-level repository metrics and summary."""

    repo_name: str
    repo_path: str
    current_branch: str
    total_commits: int
    total_contributors: int
    total_files: int
    total_insertions: int
    total_deletions: int
    first_commit_date: datetime | None
    latest_commit_date: datetime | None
    top_contributors: list[ContributorStats] = field(default_factory=list)
    top_file_types: list[FileTypeStats] = field(default_factory=list)
    activity_by_weekday: dict[str, int] = field(default_factory=dict)
    activity_by_hour: dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to a serializable dictionary."""
        data = asdict(self)
        data["first_commit_date"] = (
            self.first_commit_date.isoformat() if self.first_commit_date else None
        )
        data["latest_commit_date"] = (
            self.latest_commit_date.isoformat() if self.latest_commit_date else None
        )
        data["top_contributors"] = [c.to_dict() for c in self.top_contributors]
        data["top_file_types"] = [f.to_dict() for f in self.top_file_types]
        return data
