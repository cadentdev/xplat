# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Xplat is a cross-platform Python CLI tool for batch file management and conversion operations. Built with Python 3.12+ using Poetry for dependency management and Typer for the CLI interface.

**Current Status** (2026-02-22): Version 0.3.0. CI fully green. All mypy, ruff, bandit, and pip-audit checks pass. 74/74 tests, 98% coverage. Builds on Ubuntu, macOS, Windows with Python 3.12 and 3.13.

## Development Commands

### Environment Setup
- `poetry install` - Install dependencies and development tools
- `poetry shell` - Activate virtual environment

### Testing and Quality Assurance
- `pytest` - Run test suite
- `pytest --cov-report term-missing --cov=src/` - Run tests with coverage report
- `poetry run pytest --cov=./ --cov-report=lcov tests/` - Run tests with lcov coverage for CI

### Code Quality and Linting
- `poetry run ruff check .` - Fast linting with ruff (replaces flake8 + isort)
- `poetry run ruff format .` - Format code with ruff
- `poetry run ruff check . --fix` - Auto-fix linting issues
- `poetry run ruff check --select RUF013,B007,B008,PTH123,SIM102,SIM108` - Check specific rule categories
- `poetry run mypy .` - Type checking (0 errors as of 2026-02-19)
- `poetry run bandit -r src/` - Security linting
- `poetry run pip-audit` - Check dependencies for known vulnerabilities

### Comprehensive Quality Check
- `poetry run pytest && poetry run ruff check . && poetry run mypy . --no-error-summary` - Full QA pipeline

### Pre-commit Hooks
- `poetry run pre-commit install` - Install pre-commit hooks
- `poetry run pre-commit run --all-files` - Run all hooks on all files
- `poetry run pre-commit autoupdate` - Update hook versions

### Running the Application
- `xplat --help` - Show available commands after installation
- `poetry run python -m xplat.cli` - Run during development

### Single Test Execution
- `pytest tests/test_specific_module.py` - Run specific test file
- `pytest tests/test_specific_module.py::test_function_name` - Run specific test

### Development Workflow
1. **Initial Setup**: `poetry install && poetry run pre-commit install`
2. **Daily Development**: Pre-commit hooks run automatically on commit
3. **Manual Quality Check**: `poetry run pre-commit run --all-files`
4. **Before Push**: `poetry run pytest && poetry run ruff check . && poetry run mypy . --no-error-summary`
5. **Specific Issue Debugging**: Use targeted ruff rules for focused fixes

### Quality Metrics (2026-02-22)
- **Tests**: 74/74 passing
- **Test Coverage**: 98%
- **MyPy**: 0 errors
- **Ruff**: 0 linting or formatting issues
- **Bandit**: 0 security findings
- **pip-audit**: 0 known vulnerabilities
- **CI**: Green on all 6 matrix jobs (3 OS x 2 Python versions)

## Architecture

### Core Structure
- **CLI Layer** (`src/xplat/cli.py`): Refactored Typer-based interface with enhanced options and interactive mode
- **Business Logic Modules**:
  - `list.py` - File discovery, listing utilities, and FileInfo class
  - `rename.py` - Enhanced file renaming with `rename_file()`, `make_safe_path()`, and `safe_stem()` functions
  - `info.py` - Platform information reporting
- **Configuration** (`constants.py`): Dynamic version via `importlib.metadata`, error codes, program metadata
- **Task Tracking** (`TASK.md`): Current work items, completed items, and backlog

### Command Architecture
The CLI has been refactored with improved patterns:
1. Modular functions for error handling (`print_error()`)
2. Enhanced file listing with interactive selection (`review_files()`)
3. Structured file information display (`FileInfo` class, `print_file_data()`)
4. Separated concerns: validation, file processing, user interaction
5. Consistent error codes and user prompts

### Key Dependencies
- **Typer**: CLI framework with automatic help generation
- **pathlib**: Modern path handling (Python 3.4+)
- **colorama**: Cross-platform colored terminal output
- **importlib.metadata**: Package version reading from installed metadata (stdlib)

### Development Dependencies
- **Ruff**: Fast Python linter and formatter (replaces flake8, isort, black)
- **MyPy**: Static type checker
- **Bandit**: Security linter for common vulnerabilities
- **pip-audit**: Dependency vulnerability scanner (by Python Packaging Authority)
- **Pre-commit**: Git hook framework for automated quality checks

### File Processing Patterns
- All file operations use pathlib.Path objects
- File filtering by extension is case-sensitive
- Enhanced dry-run output with detailed formatting
- Interactive mode with per-file confirmation
- Improved error handling with proper exceptions (FileNotFoundError, FileExistsError)
- Style-based filename transformation: web (hyphens), snake (underscores), kebab, camel
- Unicode whitespace normalization, null byte rejection, filename length truncation

### Available Commands
- `info` - Platform and Python environment information
- `list` - Interactive directory listing with file selection and detailed info display
- `rename` - Style-based batch file renaming with multiple options:
  - `SOURCE` (positional): File or directory to rename (default: current directory)
  - `--style`: Naming style — `web` (default), `snake`, `kebab`, `camel`
  - `-o/--output-dir`: Output directory (optional)
  - `-e/--ext`: File extension filter (optional)
  - `-n/--dry-run`: Preview changes without modifying files
  - `-i/--interactive`: Interactive confirmation mode

## Code Style and Quality
- **Ruff**: Primary linting and formatting tool (style, imports, naming, complexity)
- **MyPy**: Static type checking (0 errors)
- **Bandit**: Security linting for common vulnerabilities
- **pip-audit**: Dependency vulnerability scanning (PyPA)
- **Pre-commit hooks**: Automated quality checks before commits

### Style Guidelines
- Snake case for functions and variables
- Upper camel case for classes
- No wildcard imports (enforced by ruff)
- Absolute imports only (enforced by ruff)
- Type hints throughout codebase (enforced by mypy)
- Max line length: 127 characters
- Max function complexity: 10 (McCabe)
- Descriptive error messages with colored output

### Migration from Sourcery
This project has migrated from Sourcery to Ruff for code quality. The transition provides:
- **10-100x faster** linting performance
- **More comprehensive** rule coverage
- **Better integration** with modern Python tooling
- **Actively maintained** by the Astral team

All previous Sourcery rules have been mapped to equivalent or better Ruff rules in the `[tool.ruff]` configuration.
