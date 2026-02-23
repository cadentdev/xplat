# Release Notes

## v0.3.0 — Style-Based Rename with Security Hardening (2026-02-22)

Your filenames should work everywhere. On any OS, in any URL, in any script. That's what xplat v0.3.0 delivers.

xplat is an open-source Python CLI that batch-renames files for cross-platform compatibility. Drop a folder of macOS screenshots with Unicode whitespace and mixed case into xplat, and out come clean, URL-safe filenames that work on Linux, Windows, and the web.

What's new in v0.3.0:

The rename command got a complete overhaul with a new style system. Four naming styles to match how you work:

- web (default): my-file-name.txt -- URL-safe, lowercase, hyphens
- snake: my_file_name.txt -- Python and filesystem conventions
- kebab: my-file-name.txt -- converts underscores to hyphens too
- camel: myFileName.txt -- for codebases that prefer camelCase

Just run: xplat rename ~/screenshots --style snake --dry-run

The CLI is simpler now. The source path is a positional argument instead of a flag. Single files, directories, or default to the current directory. Less typing, same power.

Under the hood, this release resolves two long-standing issues. Hyphens are no longer stripped from filenames (#18, open since 2023). Unicode whitespace from macOS screenshots -- the invisible characters that break shell tools and file APIs -- is now properly normalized (#29).

Security was a priority again. A red team pass uncovered and fixed:

- Filename length overflow (>255 bytes crashed the OS)
- Null byte injection bypassing normalization
- Symlink traversal at the CLI level
- Silent failures on case-only renames (macOS/Windows)
- Dry-run mode hiding target collisions
- 6 CVEs in dev dependencies (all patched)

The numbers: 74 tests at 98% coverage across 3 operating systems and 2 Python versions. Zero errors from mypy, ruff, bandit, and pip-audit. Every security finding tested, fixed, and verified before merge.

This is what happens when you combine TDD discipline with adversarial AI analysis. Write the failing tests first, implement the fix, red team the result. Repeat until nothing breaks.

github.com/cadentdev/xplat

#OpenSource #Python #CLI #DevSecOps #CrossPlatform #TDD #AgenticDevelopment #AI

## v0.2.0 — Security Hardening & Agentic Red Team (2026-02-19)

We had 32 AI agents try to break our software before we shipped it. Here's what happened.

xplat is an open-source Python CLI tool for batch file management — renaming, listing, and converting files across macOS, Linux, and Windows. If you've ever needed to sanitize a folder of filenames for web upload or script a batch rename across platforms, that's what xplat does.

For v0.2.0, we wanted to see what happens when you treat AI agents as adversaries, not just assistants. Before cutting the release, we ran a red team analysis using 32 adversarial AI agents — each one independently probing the codebase for security weaknesses from a different attack angle.

They found real vulnerabilities:

- Glob injection through user-supplied file extension filters
- Symlink exploitation in the rename pipeline
- Batch rename collision attacks that could crash mid-operation

Every finding was fixed, covered by new tests, and verified before the code hit main.

The full picture for v0.2.0:

- 32-agent adversarial security analysis with all findings resolved
- 34 pytest tests passing at 99% coverage across 3 operating systems and 2 Python versions (3.12, 3.13)
- 18 unused dependencies removed — smaller attack surface, faster installs
- Zero errors from mypy, ruff, and bandit static analysis
- 7 open issues closed in a single PR, some dating back to 2022
- Repo transferred from stratofax to cadentdev organization

We're a small team, and having 32 agents independently stress-test your code before release is the kind of leverage that changes what's possible. Every vulnerability they surfaced was one we could fix before users ever encountered it.

github.com/cadentdev/xplat

#OpenSource #Python #AgenticDevelopment #CyberSecurity #RedTeam #AI #DevSecOps

## v0.1.2 — Modernization & Typer Upgrade (2025-01-09 to 2025-09-14)

A major modernization effort that brought xplat from Python 3.9 to 3.12+, replaced legacy tooling, and rewrote the rename module.

### CLI Overhaul

- Upgraded Typer from 0.12.5 to 0.17.4, resolving critical `Parameter.make_metavar()` crash
- Migrated all CLI options to modern `Annotated[Type, typer.Option()]` syntax
- Added short-form option flags: `-s`, `-o`, `-e`, `-n`, `-i`, `-h`, `-V`
- Added interactive rename mode with per-file confirmation (`--interactive`)
- Non-interactive mode became the default — scripts work without prompts

### Rename Module Rewrite

- Rewrote `renamer.py` as `rename.py` with `rename_file()`, `make_safe_path()`, and `safe_stem()`
- Fixed TypeError crash when renaming files without extension filter (Issue #3)
- Fixed "type None" display when no extension provided (Issue #2)
- Added dry-run with detailed output formatting
- Improved error handling with proper exceptions (`FileNotFoundError`, `FileExistsError`)

### Tooling Migration

- Migrated from Sourcery to Ruff for linting and formatting (10-100x faster)
- Replaced flake8, isort, and black with Ruff
- Added pre-commit hooks (ruff, mypy, bandit)
- Removed 18 unused dependencies (optimize-images, pdf2image, pillow, shellingham, and more)
- Added CLAUDE.md and ROADMAP.md for project documentation

### Quality

- Python version requirement updated from 3.9 to 3.12+
- 17 tests passing across Ubuntu, macOS, and Windows
- MyPy type checking enabled with 0 errors
- Bandit security scanning added
- CI pipeline fixed and green on all 6 matrix jobs

## Pre-release Development History (2022-03 to 2024-12)

The foundations of xplat, built over two years of iterative development before formal versioning.

### Project Genesis (2022-03 to 2022-06)

- **2022-03-06**: Initial commit — Poetry project scaffold
- **2022-04-07**: Adopted Typer as CLI framework
- **2022-05-18**: Core commands implemented: `info` (platform reporting), `list` (directory listing), and `names` (file renaming)
- **2022-05-19**: PDF-to-image conversion module added (later removed)
- **2022-06-22**: PR #1 — First merge from `clidev` branch, established `cli.py` as app entry point
- **2022-06-23**: README with usage examples, initial bug reports filed (Issues #2, #5)

### Bug Fixes & Test Coverage (2022-07 to 2022-12)

- **2022-07-16**: Fixed TypeError in rename module, achieved full renamer test coverage
- **2022-09-21**: PRs #10, #11 — Text conversion and names module merged
- **2022-10-16**: Adopted Google Style Guide via Sourcery
- **2022-12-05**: Sourcery rules tested and refined

### Architecture & CI (2023-02 to 2023-06)

- **2023-02-26**: PR #12 — Major restructuring: constants module, errno codes, strict renaming
- **2023-03-19**: PR #14/#15 — GitHub Actions CI pipeline, list module refactored, test improvements
- **2023-03-30**: Collision detection — skip files when renamed target already exists
- **2023-04-19**: GUI experiment with tkinter (later removed from release branch)
- **2023-04-28**: Enhanced list command with interactive file selection and info display
- **2023-05-07**: Coveralls integration for coverage reporting, badge added to README
- **2023-05-22 to 2023-06-10**: Module refactoring — renamed modules to match CLI subcommands, refactored `rename_list` and `rename_files`
