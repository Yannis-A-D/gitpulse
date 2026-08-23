# ⚡ gitpulse

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/gitpulse.svg?color=blue)](https://pypi.org/project/gitpulse/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitpulse.svg)](https://pypi.org/project/gitpulse/)
[![CI Tests](https://github.com/Yannis-A-D/gitpulse/actions/workflows/test.yml/badge.svg)](https://github.com/Yannis-A-D/gitpulse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**A visual Git repository analyzer and CLI dashboard for developers.**

*Inspect commit frequency, code churn, top contributors, file distribution, and export beautiful reports in seconds.*

</div>

---

## ✨ Features

- 📊 **Visual Terminal Dashboard**: Rich colored tables, commit distribution bars, and repository health metrics.
- 👥 **Contributor Leaderboards**: Track commits, additions, deletions, and active timeframes per author.
- 📁 **File & Code Churn Analytics**: Identify most frequently modified file types and code turnover.
- 📑 **Multiple Export Formats**: Export clean **Markdown** reports or raw **JSON** data for CI pipelines.
- 🐍 **Dual-Use**: Use directly from your terminal as a CLI tool or import it as a typed Python library.
- ⚡ **Zero Heavy Dependencies**: Built with pure standard library Git integration and styled with `rich`.

---

## 🚀 Installation

Install using `pip` or `pipx`:

```bash
pip install gitpulse
```

Or install with `uv` / `pipx` for CLI use:

```bash
pipx install gitpulse
```

---

## 💻 CLI Usage

Run `gitpulse` inside any Git repository:

### 1. Repository Summary Overview
```bash
gitpulse
```
*Displays repo name, total commits, contributors, active branch, date range, and activity breakdown.*

### 2. Contributor Leaderboard
```bash
gitpulse contributors --top 10
```

### 3. File Type & Churn Breakdown
```bash
gitpulse files
```

### 4. Export Markdown / JSON Reports
```bash
# Generate a Markdown report for documentation
gitpulse report --format markdown --output repo_summary.md

# Output raw JSON for automation
gitpulse --json
```

---

## 🐍 Python Library Usage

You can also use `gitpulse` inside your own Python scripts:

```python
from gitpulse import RepoAnalyzer

# Initialize analyzer with path to any Git repo (default is current dir)
analyzer = RepoAnalyzer(".")

# Get comprehensive summary
summary = analyzer.summary()
print(f"Repository: {summary.repo_name}")
print(f"Total Commits: {summary.total_commits}")
print(f"Total Contributors: {summary.total_contributors}")

# Get contributor stats
contributors = analyzer.get_contributors(top_n=5)
for author in contributors:
    print(
        f"{author.name} ({author.email}): {author.commits} commits (+{author.insertions}/-{author.deletions})"
    )

# Export as dictionary or JSON
json_data = analyzer.to_json()
```

---

## 🛠️ Development & Contributing

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Yannis-A-D/gitpulse.git
   cd gitpulse
   ```

2. Create a virtual environment and install development dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Run tests and linters:
   ```bash
   pytest
   ruff check .
   mypy src
   ```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
