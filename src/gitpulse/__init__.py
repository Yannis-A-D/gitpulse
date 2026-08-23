"""GitPulse - A visual Git repository analyzer and dashboard."""

from gitpulse.analyzer import (
    EmptyRepositoryError,
    GitPulseError,
    NotAGitRepositoryError,
    RepoAnalyzer,
)
from gitpulse.formatters import format_markdown_report
from gitpulse.models import (
    CommitInfo,
    ContributorStats,
    FileTypeStats,
    RepoSummary,
)

__version__ = "0.1.0"

__all__ = [
    "CommitInfo",
    "ContributorStats",
    "EmptyRepositoryError",
    "FileTypeStats",
    "GitPulseError",
    "NotAGitRepositoryError",
    "RepoAnalyzer",
    "RepoSummary",
    "format_markdown_report",
]
