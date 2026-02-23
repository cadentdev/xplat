# xplat

[![Coverage Status](https://coveralls.io/repos/github/cadentdev/xplat/badge.svg?branch=main)](https://coveralls.io/github/cadentdev/xplat?branch=main)

(Coverage stats for the main branch)

## Cross-platform Python tools for batch file management and conversion at the command line

If you have to work with lots of files on different computing platforms, `xplat` is here to help. Uploading files from your notebook to a web server? Use `xplat rename` to change the file names so they won't break your web browser. Want to know more about your computer or Python installation? Use `xplat info` for a detailed system report.

Created for Python 3.12 or later, this package uses the [pathlib module, Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html), introduced in Python 3.4, to work with files on all platforms.

## xplat Features

Designed from the start to work across platforms, `xplat` includes these features:

- Extensive command-line help.
- Tested on Mac, Linux, and Windows.
- Works with individual files or directories.

## Getting Started

1. Create a fork of this repo on your computer.
2. Install Poetry if you haven't already:
   - Visit https://python-poetry.org/docs/#installation
   - Or use: `curl -sSL https://install.python-poetry.org | python3 -`
   - Verify with: `poetry --version`
3. In the root directory of this project, run `poetry install` to ensure you have all the required packages
4. Start the virtual environment: `poetry shell`
5. Run `xplat --help` for a list of subcommands and options.
6. (Optional) Run `xplat --install-completion` with the name of your shell (bash, zsh, fish, etc.) to enable tab completion.

Note: if you don't want to invoke the poetry virtual environment using `poetry shell`, you can simply prefix your commands with `poetry run`. For example, enter `poetry run xplat --help`.

## Development and Testing

### Running Tests

If the steps described above in the **Getting Started** section worked for you, you'll also be able to run the `pytest` test suite:

```bash
pytest
```

To see a code coverage report:

```bash
pytest --cov-report term-missing --cov=src/
```

### Code Quality

This project uses modern Python tooling for code quality:

```bash
# Lint and format code (replaces flake8 + isort)
poetry run ruff check .
poetry run ruff format .

# Auto-fix many linting issues
poetry run ruff check . --fix

# Type checking
poetry run mypy .

# Security scanning
poetry run bandit -r src/
poetry run pip-audit

# Comprehensive quality check
poetry run pytest && poetry run ruff check . && poetry run mypy . --no-error-summary
```

**Current Quality Status** (2026-02-22):
- Tests: 74/74 passing (100%)
- Coverage: 98%
- MyPy: 0 errors across 6 source files
- Ruff: 0 linting or formatting issues
- Bandit: 0 security findings
- pip-audit: 0 known vulnerabilities
- CI: Green on Ubuntu, macOS, Windows (Python 3.12, 3.13)

### Pre-commit Hooks (Recommended)

Set up automated code quality checks before each commit:

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run all checks manually
poetry run pre-commit run --all-files
```

Once installed, the hooks will automatically run ruff, mypy, bandit, and other quality checks before each commit.

**Development Workflow**:
1. Install dependencies: `poetry install`
2. Set up pre-commit: `poetry run pre-commit install`
3. Develop with automatic quality checks on commit
4. Before pushing: `poetry run pytest && poetry run ruff check . && poetry run mypy . --no-error-summary`

### Reporting Issues

If you find an error, please report it by creating an issue on this repo.

## Subcommands

The `xplat` utility offers several useful sub-commands (or, more simply, _commands_). Here's the current list, from `xplat --help`

```bash
Commands:
  info    Display platform information.
  list    List files in a directory, or info for a file.
  rename  Convert file names for cross-platform compatibility.
```

### info

Display platform information, from Python's perspective. Useful for troubleshooting and debugging. Here's the sample output from a Mac M1 mini:

```bash
➤ xplat info

-- Platform Information --------------------
macOS-12.4-arm64-arm-64bit

-- System Information ----------------------
System:          Darwin
Node:            My-Mac-mini.local
Release:         21.5.0
Version:         Darwin Kernel Version 21.5.0: Tue Apr 26 21:08:29 PDT 2022; root:xnu-8020.121.3~4/RELEASE_ARM64_T8101
Machine:         arm64

-- Python Information ----------------------
Python Branch:                 (not found)
Python Compiler:               Clang 13.1.6 (clang-1316.0.21.2)
Python Implementation:         CPython
Python Revision:               (not found)
Python Version:                3.9.13

-- macOS Information -----------------------
macOS Version:                 12.4
```

### list

List files in the specified directory. Especially useful to see which files you'll modify with any of the other conversion commands, since it uses the same file listing code as the other commands.

Also lists file information for individual files. Either provide the path to the file, or select a file from the list.

Some examples:

```bash
# list all the files (no directories) in your home directory
xplat list ~

# list all pdf files in ~/Downloads -- note the ext is case-sensitive
xplat list ~/Downloads/ --ext pdf
```

## rename

Convert file names for cross-platform and web compatibility using a style-based system. Four naming styles are available:

| Style | Separator | Example |
|-------|-----------|---------|
| **web** (default) | hyphens | `My File.v2.txt` → `my-file-v2.txt` |
| **snake** | underscores | `My File.v2.txt` → `my_file_v2.txt` |
| **kebab** | hyphens (converts underscores too) | `My_File.v2.txt` → `my-file-v2.txt` |
| **camel** | none | `My File.v2.txt` → `myFileV2.txt` |

All styles normalize Unicode whitespace, strip leading/trailing spaces, collapse consecutive separators, and lowercase extensions.

The source is a positional argument — pass a file, a directory, or omit it to use the current directory.

Options:

- `--style`: Naming style — `web`, `snake`, `kebab`, or `camel` (default: `web`)
- `-o, --output-dir`: Output directory to save renamed files
- `-e, --ext`: Case-sensitive file extension filter
- `-n, --dry-run`: Preview changes without modifying files
- `-i, --interactive`: Prompt for confirmation before each rename

Some examples:

```bash
# Preview name conversion for all files in ~/Downloads (web style, default)
xplat rename ~/Downloads --dry-run

# Rename using snake_case style
xplat rename ~/Downloads --style snake --dry-run

# Move and rename all PDF files from ~/Downloads to ~/temp
xplat rename ~/Downloads --output-dir ~/temp --ext pdf

# Rename a single file
xplat rename ~/Photos/My\ Photo.PNG

# Rename files in current directory with interactive confirmation
xplat rename --interactive

# Preview renaming of JPG files only using kebab-case
xplat rename ~/Photos --ext jpg --style kebab --dry-run
```

## FAQ

Some questions and answers about the `xplat` utility.

### Why doesn't xplat do X?

I've added the different features as I've needed them for my web development work. If you'd like to suggest a new feature, add an issue on this repo.

### I can already do this thing using another program on my favorite computer. Why would I want to use xplat?

Because:

- You might want to perform the same types of conversions to a larger group of files, not just one, and xplat is designed to process many files at once.
- You'd like to automate your workflow  using bash scripts.
- You have to switch from one type of computer to another and the program you used to use for converting files is not available / crazy expensive / no fun to use on the new platform.
- You want to contribute to open source.

### I can't code, but I want to help! What can I do?

- If you find a bug, let us know: please report it by creating an issue on this repo.
- You can help improve the documentation, by writing, editing, or creating diagrams.
- You can help translate the program to a different language.

### Why is xplat so slow?

Because xplat is written as a cross-platform tool, not all of the code has been compiled and optimized for your specific platform. Having said that, if you're using `xplat` to process hundreds, or thousands, of files, let us know how you're using the program and perhaps we'll code up some optimizations or add multi-threaded execution to speed things up for you.

In general, though, `xplat` was designed to run through a set of files without intervention, after you've selected your options and answered a few prompts. You can just let it run in the background or overnight while you do something else.
