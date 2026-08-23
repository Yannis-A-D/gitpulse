"""Unit tests for report formatters."""

from pathlib import Path

from gitpulse.analyzer import RepoAnalyzer
from gitpulse.formatters import format_markdown_report


def test_format_markdown_report(populated_git_repo: Path) -> None:
    analyzer = RepoAnalyzer(populated_git_repo)
    summary = analyzer.summary()
    report = format_markdown_report(summary)

    assert "# 📊 GitPulse Repository Report: `test_repo`" in report
    assert "| **Total Commits** | 3 |" in report
    assert "Alice Dev" in report
    assert "Bob Builder" in report
    assert ".py" in report
    assert ".md" in report
