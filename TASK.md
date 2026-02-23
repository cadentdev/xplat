# TASK.md - xplat Current Work Items

## Completed in v0.2.0 (2026-02-19)

### Security Hardening
- [x] **Fix `constants.py` version loading** - Replaced relative `Path("pyproject.toml")` with `importlib.metadata.version("xplat")` — was a release blocker
- [x] **Extension filter validation** - `validate_extension()` rejects glob metacharacters (`*`, `?`, `/`, `..`)
- [x] **Symlink detection** - `rename_file()` refuses to operate on symlinks
- [x] **Batch rename collision handling** - `FileExistsError` caught gracefully (skip + warn, not crash)
- [x] **Replace safety with pip-audit** - Migrated to Python Packaging Authority's actively maintained scanner

### Version & CI
- [x] **Version bumped to 0.2.0**
- [x] **21/21 tests passing** on Ubuntu, macOS, Windows (Python 3.12, 3.13)
- [x] **0 errors** across mypy, ruff, bandit

## Completed in v0.3.0 (2026-02-22)

### Style-Based Rename System
- [x] **Style system** - `--style` flag with web/snake/kebab/camel naming styles
- [x] **Positional source argument** - `xplat rename <path>` replaces `--source-dir` flag
- [x] **Single file support** - `xplat rename file.txt` renames a single file
- [x] **Current directory default** - `xplat rename` with no args uses cwd
- [x] **Preserve hyphens** - Web style (default) keeps hyphens in filenames (#18)
- [x] **Unicode whitespace** - Handles U+202F, U+00A0 from macOS screenshots (#29)
- [x] **Strip leading/trailing spaces** - Normalized before transformation

### Security Hardening (Red Team Pass)
- [x] **Null byte injection** - Null bytes normalized to spaces in `_normalize_whitespace()`
- [x] **Filename length overflow** - `safe_stem()` truncates to NAME_MAX (255 bytes)
- [x] **Symlink traversal at CLI** - CLI rejects symlinks before any file operations
- [x] **Case-only rename on case-insensitive FS** - Uses `samefile()` for macOS/Windows
- [x] **Dry-run collision detection** - Shows target exists error in dry-run mode
- [x] **Dev dependency CVEs** - Updated filelock, urllib3, virtualenv

### Quality
- [x] **74/74 tests passing** on Ubuntu, macOS, Windows (Python 3.12, 3.13)
- [x] **98% test coverage**
- [x] **0 errors** across mypy, ruff, bandit, pip-audit

## Open Items (v0.3.1+)

### Code Quality
- [ ] **Fix `info.py` builtin shadowing** - Rename `property` variable to `value` in `add_list()` to avoid shadowing Python builtin
- [ ] **Add timezone awareness** - `list.py:17` `datetime.fromtimestamp()` should use explicit timezone

### Refactoring
- [ ] **Decompose `rename` command** - `cli.py` rename function is too long; extract file discovery, validation, and confirmation into helpers
- [ ] **Simplify `print_files()` control flow** - Remove sourcery skip comment, use `len(files)` directly
- [ ] **Split `print_selected_info()`** - Separate input validation, file display, and user prompting
- [ ] **Modernize `check_dir()`/`check_file()` return types** - Replace `(bool, str)` tuples with proper exception raising
- [ ] **Remove stale test docstrings** - References to "should FAIL with current Typer 0.9.x" (tests pass now)

### Documentation
- [ ] **Create CONTRIBUTING.md** - Development setup, testing, code style guide
- [ ] **Add GitHub issue templates** - Bug report, feature request
- [ ] **Remove or refresh BASELINE-REPORT.md** - Frozen at September 2025 state

## Backlog (from ROADMAP.md)

### CLI Enhancements
- [ ] Add logging with verbosity levels
- [ ] Implement plugin architecture
- [ ] `list`: Use current directory as default when no path specified
- [ ] `info`: Separate data collection from formatting
- [ ] `info`: Export to JSON format

### Infrastructure
- [ ] Evaluate replacing `colorama` + raw `typer.secho` with `rich` for better terminal output
- [ ] Consider adding `py.typed` marker for downstream type checking consumers
