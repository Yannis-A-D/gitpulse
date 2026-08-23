"""Unit and integration tests for CLI interface."""

from pathlib import Path

from gitpulse.cli import main


def test_cli_summary(populated_git_repo: Path) -> None:
    exit_code = main(["-p", str(populated_git_repo), "summary"])
    assert exit_code == 0


def test_cli_contributors(populated_git_repo: Path) -> None:
    exit_code = main(["-p", str(populated_git_repo), "contributors", "--top", "5"])
    assert exit_code == 0


def test_cli_files(populated_git_repo: Path) -> None:
    exit_code = main(["-p", str(populated_git_repo), "files"])
    assert exit_code == 0


def test_cli_json(populated_git_repo: Path) -> None:
    exit_code = main(["-p", str(populated_git_repo), "--json"])
    assert exit_code == 0


def test_cli_report_markdown(populated_git_repo: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "report.md"
    args = ["-p", str(populated_git_repo), "report", "-f", "markdown", "-o", str(out_file)]
    exit_code = main(args)
    assert exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "GitPulse Repository Report" in content


def test_cli_report_json(populated_git_repo: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "report.json"
    exit_code = main(["-p", str(populated_git_repo), "report", "-f", "json", "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert '"total_commits": 3' in content


def test_cli_invalid_repo(tmp_path: Path) -> None:
    empty_dir = tmp_path / "not_git"
    empty_dir.mkdir()
    exit_code = main(["-p", str(empty_dir)])
    assert exit_code == 1
