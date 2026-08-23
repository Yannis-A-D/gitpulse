# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-24

### Added
- Initial release of `gitpulse`.
- `RepoAnalyzer` core engine for querying git commit history, code churn, and contributor stats.
- Visual CLI terminal dashboard powered by `rich` (`gitpulse`, `gitpulse contributors`, `gitpulse report`).
- Support for JSON export and formatted Markdown report generation.
- Full type annotations and dataclass models.
- Comprehensive test suite with pytest.
- GitHub Actions CI/CD and PyPI Trusted Publishing workflows.
