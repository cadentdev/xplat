# Roadmap for xplat

## Critical Typer Compatibility Issues ✅ RESOLVED

- [x] **Fix Typer help system crashes** - `TypeError: Parameter.make_metavar()` compatibility issue ✅
  - [x] Upgrade Typer from 0.12.5 to 0.17.4 (latest stable version)
  - [x] Test all help functionality: `--help`, `-h`, command-specific help
  - [x] Resolve Click version compatibility (Click 8.2.1 works with Typer 0.17.4)
  - [x] Migrate to modern Annotated syntax for Typer 0.17+ compatibility
- [x] **Resolve TDD test failures** - 5/5 help tests now passing ✅
  - [x] `test_app_help()` - Main application help ✅
  - [x] `test_info_help()` - Info command help ✅
  - [x] `test_list_help()` - List command help ✅
  - [x] `test_rename_help()` - Rename command help ✅
  - [x] `test_help_flag_short()` - Short flag `-h` support ✅

## Update dependencies

- [x] Remove Sourcery dependency and replace with ruff
- [x] Update Python version requirements from 3.9 to 3.12
- [x] Remove unused dependencies (optimize-images, pdf2image, shellingham, importlib-resources)
- [x] Remove redundant dev dependencies (black, flake8, isort, pylint) - replaced by Ruff
- [x] Fix MyPy pre-commit integration dependency conflicts (using local poetry run mypy)
- [x] Resolve remaining Safety + Typer compatibility after Typer upgrade ✅
- [x] Check for additional outdated dependencies
- [x] Update old dependencies to modern versions
  - [x] Removed `tomli` (dead code — `tomllib` built into Python 3.11+)
  - [x] Updated `safety` from 1.10.3 to 3.7.0 (migrated to `safety scan`)
  - [x] Updated `pytest` to ^8.0.0, `pytest-cov` to ^6.0.0
  - [x] Updated `ruff` target-version from py39 to py312

## Code Quality Improvements

- [x] Fix remaining type hint issues (add `Optional` where needed)
  - [x] `src/xplat/cli.py` - 6 implicit Optional parameters
  - [x] `src/xplat/rename.py` - 2 implicit Optional parameters
  - [x] `src/xplat/list.py` - 1 implicit Optional parameter
- [x] Address critical Ruff linting suggestions (5 core issues)
  - [x] Convert if/else blocks to ternary operators where appropriate (SIM108)
  - [x] Fix unused loop variables (B007)
  - [x] Simplify nested if statements (SIM102)
  - [x] Replace `open()` with `Path.open()` in tests and constants (PTH123)
- [x] Resolve remaining MyPy type checking errors (11 issues) ✅
  - [x] Fix missing return statement and float/int type in `format_bytes()`
  - [x] Rename `list()` to `list_files()` to avoid builtin type name collision
  - [x] Fix `Optional[str]` parameter handling in `print_header()`
  - [x] Add `type: ignore` for `tomli` compatibility import (then removed entirely)

## Development Workflow

- [x] Implement modern Python tooling stack (Ruff, Black, Bandit, Pre-commit)
- [x] Create comprehensive pre-commit hooks
- [x] Update documentation (CLAUDE.md, README.md)
- [ ] Create development contribution guide
- [ ] Add GitHub issue templates

## Performance and Maintenance

- [x] **Dependency cleanup completed** - Removed 18 unused dependencies
  - [x] Eliminated image processing dependencies (optimize-images, pdf2image, pillow)
  - [x] Streamlined dev tooling (consolidated to Ruff + MyPy + Bandit + Safety)
  - [x] Reduced security surface area by removing unused packages
- [ ] Address remaining B008 warnings (Typer function calls in defaults)
  - Note: These are standard Typer patterns - may resolve with Typer upgrade
- [x] Update remaining vulnerable dependencies after Typer upgrade ✅
  - [x] ~~black 23.1.0~~ - Removed (replaced by Ruff)
  - [x] ~~pillow 9.4.0~~ - Removed (not used)
  - [x] Updated all dev/test dependencies to current versions
- [x] Consider pytest dependency updates — upgraded to pytest ^8.0.0 ✅
- [x] Evaluate test coverage improvement opportunities (currently 88%) — now 98% (74 tests)
- [ ] **Performance improvements from dependency reduction**
  - [x] Faster installs with 18 fewer dependencies
  - [x] Smaller Docker images / deployment footprint
  - [x] Reduced potential for dependency conflicts

## To Do - CLI

Updates to the CLI interface, by module.

### cli

- [ ] add logging to the CLI
- [ ] implement plugin architecture

### list

- [ ] Use the current directory if no directory is specified

### info

- [ ] separate data collection from formattting
- [ ] export to JSON format

### rename

- [x] Make the source directory the default (no option flag required) — positional `source` arg
- [x] Use the current directory if no source directory is specified — defaults to cwd
- [x] Support conversion of a single file — `source.is_file()` path
- [x] Keep hyphens ("-") in file names — web style (default) preserves hyphens (#18)
- [x] Remove leading, trailing spaces from file names — `_normalize_whitespace()` strips
- [x] Handle Unicode whitespace (U+202F, U+00A0, etc.) — `re.sub(r"\s", ...)` (#29)
- [x] Style system: `--style` flag with web/snake/kebab/camel options

## Recent Achievements (2026-02-19)

### ✅ v0.2.0 Release Prep — Security Hardening & Release Blocker Fix

**Security hardening (red team analysis → 4 fixes):**
- Fixed `constants.py` release blocker: replaced fragile `Path("pyproject.toml")` with `importlib.metadata.version()` — tool now works from any directory
- Added `validate_extension()` to reject glob metacharacters in extension filter
- Added symlink detection in `rename_file()` — refuses to operate on symlinks
- Batch rename now catches `FileExistsError` gracefully (skip + warn, no crash)
- Replaced `safety` with `pip-audit` (Python Packaging Authority's actively maintained scanner)

**Quality Metrics:**
- 21/21 tests passing (4 new: extension validation, symlink rejection, version metadata, invalid ext CLI)
- 87% code coverage
- 0 mypy errors, 0 ruff errors, 0 bandit findings
- CI green on all 6 matrix jobs (3 OS x 2 Python versions)

### ✅ CI Pipeline Fixed and Green

Resolved all CI failures on release/candidate-01 across all 6 matrix jobs:

**MyPy Type Checking (11 errors → 0):**
- Renamed `list()` command to `list_files()` with `@app.command(name="list")` to avoid shadowing Python's builtin `list` type
- Fixed `format_bytes()` missing return statement and float/int type mismatch
- Fixed `print_header()` to accept `str | None`
- Removed dead `tomli` fallback import from `constants.py`

**Dependency Modernization:**
- Removed `tomli` dependency (dead code since Python ^3.12 requirement)
- Updated `pytest` ^7 → ^8, `pytest-cov` ^4 → ^6
- Updated ruff target-version from py39 → py312
- Modernized all `Optional[X]` to `X | None` throughout codebase

## Previous Achievements (2025-09-14)

### ✅ Typer Compatibility Resolution

Successfully resolved critical Typer compatibility issues using Test-Driven Development:

**Technical Achievement:**
- Upgraded Typer from 0.12.5 → 0.17.4 (latest stable)
- Migrated to modern `Annotated[Type, typer.Option(...)]` syntax
- Fixed `Parameter.make_metavar() missing context argument` error
- Enhanced CLI with better help text and `-h` short flag support

**TDD Success:**
- Created 5 comprehensive TDD tests targeting help functionality
- All tests now pass (100% success rate)
- Validated complete fix with full regression testing (17/17 tests pass)

**Impact:**
- Help system fully functional: `--help` and `-h` work for all commands
- Modern codebase compatible with latest Typer best practices
- Improved developer experience and user interface
