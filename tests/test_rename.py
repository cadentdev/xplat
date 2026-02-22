"""Tests for the rename module functionality."""

import pytest

from xplat import rename
from xplat.rename import Style


@pytest.fixture
def test_dirs(tmp_path):
    """Create and return test directories using pytest tmp_path."""
    output_path = tmp_path / "target"
    output_path.mkdir()
    return tmp_path, output_path


@pytest.fixture
def test_files(test_dirs):
    """Create and return test files."""
    test_path, _ = test_dirs

    file1 = test_path / "Space to Delim.test.FILE.TXT"
    file2 = test_path / "Another.Complex File.NAME.txt"

    file1.touch()
    file2.touch()

    return file1, file2


def test_safe_stem():
    """Test filename stem transformation with default web style."""
    # Test basic transformation (web style: spaces→hyphens, dots→hyphens, lowercase)
    assert rename.safe_stem("Hello World.test") == "hello-world-test"

    # Test multiple spaces and dots
    assert rename.safe_stem("This..Has...Lots.Of..Dots") == "this-has-lots-of-dots"

    # Test multiple delimiters get collapsed
    assert rename.safe_stem("Too--Many---Delims") == "too-many-delims"


# --- Unicode whitespace tests (#29) ---


def test_safe_stem_unicode_nbsp():
    """U+00A0 no-break space is normalized and converted."""
    assert rename.safe_stem("hello\u00a0world") == "hello-world"


def test_safe_stem_unicode_narrow_nbsp():
    """U+202F narrow no-break space (macOS screenshot) is normalized."""
    assert rename.safe_stem("Screenshot\u202f2024-01-15") == "screenshot-2024-01-15"


# --- Hyphen preservation tests (#18) ---


def test_safe_stem_web_preserves_hyphens():
    """Web style keeps hyphens intact."""
    assert rename.safe_stem("my-file", style=Style.web) == "my-file"


def test_safe_stem_snake_converts_hyphens():
    """Snake style converts hyphens to underscores."""
    assert rename.safe_stem("my-file", style=Style.snake) == "my_file"


# --- Style behavior tests ---


def test_safe_stem_web_default():
    """Default style is web-safe: spaces→hyphens, dots→hyphens, lowercase."""
    assert rename.safe_stem("My File.v2") == "my-file-v2"


def test_safe_stem_snake():
    """Snake style: spaces→underscores, dots→underscores, lowercase."""
    assert rename.safe_stem("My File.v2", style=Style.snake) == "my_file_v2"


def test_safe_stem_kebab():
    """Kebab style: underscores→hyphens, spaces→hyphens, dots→hyphens."""
    assert rename.safe_stem("My_File.v2", style=Style.kebab) == "my-file-v2"


def test_safe_stem_camel():
    """Camel style: remove separators, produce camelCase."""
    assert rename.safe_stem("My File.v2", style=Style.camel) == "myFileV2"


# --- Edge case tests ---


def test_safe_stem_leading_trailing():
    """Leading and trailing whitespace stripped."""
    assert rename.safe_stem("  hello  ") == "hello"


def test_safe_stem_consecutive_delims():
    """Consecutive delimiters collapsed to single."""
    assert rename.safe_stem("a---b") == "a-b"


def test_safe_stem_empty_string():
    """Empty string returns empty string."""
    assert rename.safe_stem("") == ""


def test_safe_stem_all_special_chars():
    """String of only special chars returns empty."""
    assert rename.safe_stem("!!!") == ""


# --- make_safe_path with style ---


def test_make_safe_path(test_dirs):
    """Test safe path creation with default web style."""
    test_path, target_dir = test_dirs

    # Test in same directory (web style: hyphens)
    orig_path = test_path / "Test File.TXT"
    safe_path = rename.make_safe_path(orig_path)
    assert safe_path.name == "test-file.txt"
    assert safe_path.parent == test_path

    # Test with target directory
    safe_path = rename.make_safe_path(orig_path, target_dir)
    assert safe_path.name == "test-file.txt"
    assert safe_path.parent == target_dir


def test_make_safe_path_with_style(test_dirs):
    """Test that style propagates through make_safe_path."""
    test_path, _ = test_dirs
    orig_path = test_path / "Test File.TXT"

    safe_path = rename.make_safe_path(orig_path, style=Style.snake)
    assert safe_path.name == "test_file.txt"

    safe_path = rename.make_safe_path(orig_path, style=Style.kebab)
    assert safe_path.name == "test-file.txt"

    safe_path = rename.make_safe_path(orig_path, style=Style.camel)
    assert safe_path.name == "testFile.txt"


def test_rename_file_errors(test_dirs, test_files):
    """Test error conditions for rename_file."""
    test_path, target_dir = test_dirs
    test_file, _ = test_files

    # Test non-existent file
    bad_file = test_path / "not_a_file.tmp"
    with pytest.raises(FileNotFoundError):
        rename.rename_file(bad_file)

    # Test invalid target directory
    bad_dir = test_path / "not_a_dir"
    with pytest.raises(NotADirectoryError):
        rename.rename_file(test_file, bad_dir)

    # Test file already exists
    # First, create a file with the name that would result from renaming test_file
    # Web style default: "Space to Delim.test.FILE.TXT" → "space-to-delim-test-file.txt"
    existing_file = target_dir / "space-to-delim-test-file.txt"
    existing_file.touch()
    with pytest.raises(FileExistsError):
        rename.rename_file(test_file, target_dir)


def test_rename_file_rejects_symlink(test_dirs):
    """Test that rename_file refuses to operate on symlinks."""
    test_path, _ = test_dirs
    real_file = test_path / "real_file.txt"
    real_file.write_text("content")
    symlink = test_path / "link_to_file.txt"
    symlink.symlink_to(real_file)

    with pytest.raises(OSError, match="symlink"):
        rename.rename_file(symlink)


def test_rename_file_success(test_dirs, test_files):
    """Test successful file renaming operations."""
    test_path, target_dir = test_dirs
    test_file, _ = test_files

    # Test rename in same directory (web style: hyphens)
    new_path = rename.rename_file(test_file)
    assert new_path.exists()
    assert new_path.name == "space-to-delim-test-file.txt"
    assert new_path.parent == test_path

    # Create new file for target dir test
    new_file = test_path / "Move.This.File.TXT"
    new_file.touch()

    # Test rename to target directory
    moved_path = rename.rename_file(new_file, target_dir)
    assert moved_path.exists()
    assert moved_path.name == "move-this-file.txt"
    assert moved_path.parent == target_dir


# --- Additional edge case tests ---


def test_safe_stem_already_safe():
    """Already-safe input is returned unchanged (idempotent)."""
    assert rename.safe_stem("already-safe") == "already-safe"
    assert rename.safe_stem("already_safe", style=Style.snake) == "already_safe"
    assert rename.safe_stem("already-safe", style=Style.kebab) == "already-safe"
    assert rename.safe_stem("alreadySafe", style=Style.camel) == "alreadysafe"


def test_safe_stem_mixed_unicode_whitespace():
    """Mix of Unicode whitespace types all normalized."""
    # tab + no-break space + narrow no-break space
    assert rename.safe_stem("a\tb\u00a0c\u202fd") == "a-b-c-d"


def test_safe_stem_tabs():
    """Tab characters are treated as whitespace."""
    assert rename.safe_stem("hello\tworld") == "hello-world"


def test_safe_stem_only_whitespace():
    """String of only whitespace returns empty."""
    assert rename.safe_stem("   \t\n  ") == ""


def test_safe_stem_numeric_only():
    """Purely numeric stems are preserved."""
    assert rename.safe_stem("12345") == "12345"


def test_safe_stem_single_char():
    """Single character is preserved."""
    assert rename.safe_stem("a") == "a"


def test_make_safe_path_no_extension(test_dirs):
    """File with no extension gets safe stem only."""
    test_path, _ = test_dirs
    orig_path = test_path / "Makefile"
    safe_path = rename.make_safe_path(orig_path)
    assert safe_path.name == "makefile"


def test_make_safe_path_empty_stem_raises(test_dirs):
    """File that produces empty stem raises ValueError."""
    test_path, _ = test_dirs
    orig_path = test_path / "!!!.txt"
    with pytest.raises(ValueError, match="empty stem"):
        rename.make_safe_path(orig_path)


def test_rename_file_empty_stem_raises(test_dirs):
    """rename_file raises ValueError for filenames that produce empty stems."""
    test_path, _ = test_dirs
    bad_file = test_path / "!!!.txt"
    bad_file.write_text("content")
    with pytest.raises(ValueError, match="empty stem"):
        rename.rename_file(bad_file)
