"""Command-line interface for gitpulse."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gitpulse import __version__
from gitpulse.analyzer import GitPulseError, RepoAnalyzer
from gitpulse.formatters import format_markdown_report

# Ensure Windows terminals properly render unicode characters
for stream in (sys.stdout, sys.stderr):
    reconfigure_fn = getattr(stream, "reconfigure", None)
    if callable(reconfigure_fn):
        try:
            reconfigure_fn(encoding="utf-8", errors="replace")
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="⚡ Visual Git repository analyzer and dashboard.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-p",
        "--path",
        default=".",
        help="Path to the Git repository (default: current working directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON data instead of terminal formatting.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: summary (default)
    subparsers.add_parser("summary", help="Display full repository summary dashboard.")

    # Command: contributors
    contrib_parser = subparsers.add_parser(
        "contributors", help="Display contributor leaderboards and statistics."
    )
    contrib_parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=10,
        help="Number of top contributors to display (default: 10).",
    )

    # Command: files
    subparsers.add_parser("files", help="Display tracked file types and distribution.")

    # Command: report
    report_parser = subparsers.add_parser("report", help="Export summary as a formatted report.")
    report_parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report export format (default: markdown).",
    )
    report_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Optional file path to save the generated report.",
    )

    return parser


def print_summary_dashboard(analyzer: RepoAnalyzer, console: Console) -> None:
    """Render a visual terminal dashboard for the repository summary."""
    summary = analyzer.summary()

    title_left = "[bold cyan]⚡ GitPulse Dashboard[/bold cyan]"
    dashboard_title = f"{title_left} :: [bold white]{summary.repo_name}[/bold white]"
    console.print(
        Panel.fit(
            f"{dashboard_title}\n"
            f"[dim]Branch:[/dim] [green]{summary.current_branch}[/green] | "
            f"[dim]Path:[/dim] {summary.repo_path}",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    # Overview Metrics Table
    first_date = (
        summary.first_commit_date.strftime("%Y-%m-%d") if summary.first_commit_date else "N/A"
    )
    last_date = (
        summary.latest_commit_date.strftime("%Y-%m-%d") if summary.latest_commit_date else "N/A"
    )

    metrics_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric", style="bold white")
    metrics_table.add_column("Value", justify="right", style="green")

    metrics_table.add_row("Total Commits", f"{summary.total_commits:,}")
    metrics_table.add_row("Contributors", f"{summary.total_contributors:,}")
    metrics_table.add_row("Tracked Files", f"{summary.total_files:,}")
    metrics_table.add_row("Lines Added (+)", f"+{summary.total_insertions:,}", style="green")
    metrics_table.add_row("Lines Deleted (-)", f"-{summary.total_deletions:,}", style="red")
    metrics_table.add_row("Active Period", f"{first_date} → {last_date}", style="yellow")

    console.print("\n[bold]📈 Overview Metrics[/bold]")
    console.print(metrics_table)

    # Contributors Table
    print_contributors_table(analyzer, console, top_n=5)

    # Activity by Weekday
    console.print("\n[bold]📅 Commit Frequency by Weekday[/bold]")
    weekday_table = Table(box=box.SIMPLE, show_header=False)
    weekday_table.add_column("Day", style="bold cyan", width=12)
    weekday_table.add_column("Commits", justify="right", width=8)
    weekday_table.add_column("Distribution", style="green")

    max_day_commits = (
        max(summary.activity_by_weekday.values()) if summary.activity_by_weekday else 1
    )
    for day, count in summary.activity_by_weekday.items():
        bar_len = int((count / max_day_commits) * 25) if max_day_commits > 0 else 0
        bar = "█" * bar_len
        weekday_table.add_row(day, f"{count:,}", f"[green]{bar}[/green]")

    console.print(weekday_table)


def print_contributors_table(analyzer: RepoAnalyzer, console: Console, top_n: int = 10) -> None:
    """Render a table of top contributors."""
    contributors = analyzer.get_contributors(top_n=top_n)

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title=f"👥 Top {len(contributors)} Contributors",
        title_justify="left",
    )
    table.add_column("Contributor", style="bold white")
    table.add_column("Email", style="dim")
    table.add_column("Commits", justify="right", style="cyan")
    table.add_column("Share", justify="right", style="yellow")
    table.add_column("Lines (+)", justify="right", style="green")
    table.add_column("Lines (-)", justify="right", style="red")

    for author in contributors:
        table.add_row(
            author.name,
            author.email,
            f"{author.commits:,}",
            f"{author.percentage_of_commits:.1f}%",
            f"+{author.insertions:,}",
            f"-{author.deletions:,}",
        )

    console.print(table)


def print_files_table(analyzer: RepoAnalyzer, console: Console) -> None:
    """Render a table of tracked file types."""
    file_types = analyzer.get_file_type_breakdown(top_n=12)

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold blue",
        title="📁 File Extensions Breakdown",
        title_justify="left",
    )
    table.add_column("Extension", style="bold white")
    table.add_column("File Count", justify="right", style="cyan")
    table.add_column("Percentage", justify="right", style="green")
    table.add_column("Bar", style="magenta")

    for ftype in file_types:
        bar_len = int(ftype.percentage / 4)
        bar = "■" * bar_len
        table.add_row(
            ftype.extension,
            f"{ftype.count:,}",
            f"{ftype.percentage:.1f}%",
            bar,
        )

    console.print(table)


def main(argv: list[str] | None = None) -> int:
    """Main entrypoint for CLI command execution."""
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()

    try:
        analyzer = RepoAnalyzer(args.path)

        if args.json:
            console.print(analyzer.to_json())
            return 0

        command = args.command or "summary"

        if command == "summary":
            print_summary_dashboard(analyzer, console)
        elif command == "contributors":
            print_contributors_table(analyzer, console, top_n=args.top)
        elif command == "files":
            print_files_table(analyzer, console)
        elif command == "report":
            if args.format == "json":
                report_content = analyzer.to_json()
            else:
                summary = analyzer.summary()
                report_content = format_markdown_report(summary)

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(report_content, encoding="utf-8")
                saved_msg = f"[bold green]✓ Report saved to:[/bold green] {output_path.resolve()}"
                console.print(saved_msg)
            else:
                console.print(report_content)

        return 0

    except GitPulseError as err:
        err_console = Console(stderr=True)
        err_console.print(f"[bold red]GitPulse Error:[/bold red] {err}")
        return 1
    except KeyboardInterrupt:
        console.print("\n[dim]Aborted by user.[/dim]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
