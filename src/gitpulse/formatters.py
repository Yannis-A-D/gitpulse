"""Formatters for exporting repository summaries into Markdown and other formats."""

from __future__ import annotations

from gitpulse.models import RepoSummary


def format_markdown_report(summary: RepoSummary) -> str:
    """Generate a clean, structured Markdown report from a RepoSummary object."""
    first_date_str = (
        summary.first_commit_date.strftime("%Y-%m-%d %H:%M") if summary.first_commit_date else "N/A"
    )
    last_date_str = (
        summary.latest_commit_date.strftime("%Y-%m-%d %H:%M")
        if summary.latest_commit_date
        else "N/A"
    )

    lines: list[str] = [
        f"# 📊 GitPulse Repository Report: `{summary.repo_name}`",
        "",
        f"> Generated for repository at `{summary.repo_path}` (Branch: `{summary.current_branch}`)",
        "",
        "## 📈 Overview Metrics",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Total Commits** | {summary.total_commits:,} |",
        f"| **Total Contributors** | {summary.total_contributors:,} |",
        f"| **Tracked Files** | {summary.total_files:,} |",
        f"| **Lines Added (+)** | {summary.total_insertions:,} |",
        f"| **Lines Deleted (-)** | {summary.total_deletions:,} |",
        f"| **First Commit** | {first_date_str} |",
        f"| **Latest Commit** | {last_date_str} |",
        "",
        "## 👥 Top Contributors",
        "",
        "| Contributor | Email | Commits | % of Commits | Lines Added (+) | Lines Deleted (-) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for author in summary.top_contributors:
        pct = f"{author.percentage_of_commits:.1f}%"
        lines.append(
            f"| **{author.name}** | `{author.email}` | {author.commits:,} | "
            f"{pct} | +{author.insertions:,} | -{author.deletions:,} |"
        )

    lines.extend([
        "",
        "## 📁 File Types Breakdown",
        "",
        "| Extension | Count | Percentage |",
        "| :--- | :--- | :--- |",
    ])

    for ftype in summary.top_file_types:
        lines.append(f"| `{ftype.extension}` | {ftype.count:,} | {ftype.percentage:.1f}% |")

    lines.extend([
        "",
        "## 📅 Activity by Day of the Week",
        "",
        "| Day | Commits |",
        "| :--- | :--- |",
    ])

    for day, count in summary.activity_by_weekday.items():
        bar_size = max(1, int((count / summary.total_commits) * 30))
        bar = "█" * bar_size if summary.total_commits > 0 and count > 0 else ""
        lines.append(f"| {day} | {count:,} `{bar}` |")

    lines.append("")
    return "\n".join(lines)
