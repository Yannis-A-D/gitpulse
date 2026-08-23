"""Core repository analyzer for extracting Git statistics."""

from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gitpulse.models import (
    CommitInfo,
    ContributorStats,
    FileTypeStats,
    RepoSummary,
)


class GitPulseError(Exception):
    """Base exception for GitPulse errors."""


class NotAGitRepositoryError(GitPulseError):
    """Raised when the specified directory is not a Git repository."""


class EmptyRepositoryError(GitPulseError):
    """Raised when the Git repository has no commits."""


class RepoAnalyzer:
    """Analyzes a local Git repository and computes metrics and summaries."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        """Initialize the analyzer for a repository at `repo_path`."""
        self.repo_path = Path(repo_path).resolve()
        self._validate_git_repo()

    def _run_git(self, args: list[str]) -> str:
        """Execute a git command safely in the repository directory."""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError as err:
            msg = "Git executable not found on system PATH."
            raise GitPulseError(msg) from err

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise GitPulseError(f"Git command failed: {' '.join(cmd)}\n{stderr}")

        return result.stdout

    def _validate_git_repo(self) -> None:
        """Verify that the path is inside a Git repository."""
        if not self.repo_path.exists():
            raise NotAGitRepositoryError(f"Directory does not exist: {self.repo_path}")
        try:
            output = self._run_git(["rev-parse", "--is-inside-work-tree"])
            if output.strip() != "true":
                raise NotAGitRepositoryError(f"Not a git repository: {self.repo_path}")
        except GitPulseError as err:
            raise NotAGitRepositoryError(f"Not a git repository: {self.repo_path}") from err

    def get_current_branch(self) -> str:
        """Return the current checked-out branch or commit."""
        try:
            branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
            return branch if branch else "HEAD"
        except GitPulseError:
            return "unknown"

    def get_repo_name(self) -> str:
        """Return the repository name from directory or remote URL."""
        try:
            remote_url = self._run_git(["config", "--get", "remote.origin.url"]).strip()
            if remote_url:
                name = remote_url.rstrip("/").split("/")[-1]
                if name.endswith(".git"):
                    name = name[:-4]
                return name
        except GitPulseError:
            pass
        return self.repo_path.name

    def get_tracked_files(self) -> list[str]:
        """Return a list of all tracked files in the repository."""
        try:
            output = self._run_git(["ls-files"])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except GitPulseError:
            return []

    def get_file_type_breakdown(self, top_n: int = 8) -> list[FileTypeStats]:
        """Calculate statistics for file extensions in the repository."""
        files = self.get_tracked_files()
        if not files:
            return []

        ext_counts: Counter[str] = Counter()
        for f in files:
            ext = Path(f).suffix.lower()
            ext_name = ext if ext else "[no ext]"
            ext_counts[ext_name] += 1

        total_files = len(files)
        top_exts = ext_counts.most_common(top_n)

        return [
            FileTypeStats(
                extension=ext,
                count=count,
                percentage=(count / total_files) * 100.0,
            )
            for ext, count in top_exts
        ]

    def get_commits(self, max_count: int | None = None) -> list[CommitInfo]:
        """Parse commits including author, timestamp, insertions, and deletions."""
        # Format: %H%x00%an%x00%ae%x00%aI%x00%s
        # followed by --numstat
        cmd = ["log", "--numstat", "--pretty=format:COMMIT_START%x00%H%x00%an%x00%ae%x00%aI%x00%s"]
        if max_count:
            cmd.extend(["-n", str(max_count)])

        try:
            raw_log = self._run_git(cmd)
        except GitPulseError as err:
            if "does not have any commits" in str(err) or "bad default revision" in str(err):
                raise EmptyRepositoryError("Repository has no commits.") from err
            raise

        if not raw_log.strip():
            return []

        commits: list[CommitInfo] = []
        raw_entries = raw_log.split("COMMIT_START\x00")

        for entry in raw_entries:
            if not entry.strip():
                continue

            lines = entry.strip().splitlines()
            header_line = lines[0]
            parts = header_line.split("\x00")

            if len(parts) < 5:
                continue

            commit_hash, author_name, author_email, iso_time, message = parts[:5]

            try:
                dt = datetime.fromisoformat(iso_time)
            except ValueError:
                dt = datetime.now(timezone.utc)

            insertions = 0
            deletions = 0
            files_changed = 0

            for stat_line in lines[1:]:
                stat_parts = stat_line.strip().split("\t")
                if len(stat_parts) >= 3:
                    ins_str, del_str, _ = stat_parts[:3]
                    if ins_str.isdigit():
                        insertions += int(ins_str)
                    if del_str.isdigit():
                        deletions += int(del_str)
                    files_changed += 1

            commits.append(
                CommitInfo(
                    hash=commit_hash,
                    author_name=author_name,
                    author_email=author_email,
                    timestamp=dt,
                    message=message,
                    insertions=insertions,
                    deletions=deletions,
                    files_changed=files_changed,
                )
            )

        return commits

    def get_contributors(self, top_n: int | None = None) -> list[ContributorStats]:
        """Aggregate statistics per contributor."""
        commits = self.get_commits()
        if not commits:
            return []

        author_data: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "name": "",
                "email": "",
                "commits": 0,
                "insertions": 0,
                "deletions": 0,
                "first_commit": datetime.max.replace(tzinfo=timezone.utc),
                "last_commit": datetime.min.replace(tzinfo=timezone.utc),
            }
        )

        total_commits = len(commits)

        for commit in commits:
            key = commit.author_email.lower().strip() or commit.author_name.lower().strip()
            data = author_data[key]
            data["name"] = commit.author_name
            data["email"] = commit.author_email
            data["commits"] += 1
            data["insertions"] += commit.insertions
            data["deletions"] += commit.deletions

            ts = commit.timestamp
            if ts < data["first_commit"]:
                data["first_commit"] = ts
            if ts > data["last_commit"]:
                data["last_commit"] = ts

        stats_list: list[ContributorStats] = []
        for data in author_data.values():
            percentage = (data["commits"] / total_commits) * 100.0 if total_commits > 0 else 0.0
            stats_list.append(
                ContributorStats(
                    name=data["name"],
                    email=data["email"],
                    commits=data["commits"],
                    insertions=data["insertions"],
                    deletions=data["deletions"],
                    first_commit=data["first_commit"],
                    last_commit=data["last_commit"],
                    percentage_of_commits=percentage,
                )
            )

        # Sort by commit count descending
        stats_list.sort(key=lambda s: s.commits, reverse=True)

        if top_n is not None:
            return stats_list[:top_n]
        return stats_list

    def summary(self) -> RepoSummary:
        """Compute full repository summary metrics."""
        commits = self.get_commits()
        if not commits:
            raise EmptyRepositoryError("Repository has no commits.")

        contributors = self.get_contributors()
        file_types = self.get_file_type_breakdown()
        files = self.get_tracked_files()

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        activity_by_weekday: dict[str, int] = {day: 0 for day in weekdays}
        activity_by_hour: dict[int, int] = {hour: 0 for hour in range(24)}

        total_insertions = 0
        total_deletions = 0

        for commit in commits:
            day_name = commit.timestamp.strftime("%A")
            if day_name in activity_by_weekday:
                activity_by_weekday[day_name] += 1

            hour = commit.timestamp.hour
            activity_by_hour[hour] += 1

            total_insertions += commit.insertions
            total_deletions += commit.deletions

        first_commit_date = min(c.timestamp for c in commits)
        latest_commit_date = max(c.timestamp for c in commits)

        return RepoSummary(
            repo_name=self.get_repo_name(),
            repo_path=str(self.repo_path),
            current_branch=self.get_current_branch(),
            total_commits=len(commits),
            total_contributors=len(contributors),
            total_files=len(files),
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            first_commit_date=first_commit_date,
            latest_commit_date=latest_commit_date,
            top_contributors=contributors[:10],
            top_file_types=file_types,
            activity_by_weekday=activity_by_weekday,
            activity_by_hour=activity_by_hour,
        )

    def to_json(self, indent: int = 2) -> str:
        """Return the repository summary as a formatted JSON string."""
        return json.dumps(self.summary().to_dict(), indent=indent)
