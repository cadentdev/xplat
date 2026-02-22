"""
Tests for xplat.cli. Testing here is preferred as the tests
at this level are effectively integration tests, but also
are unit tests for the dependent modules.
"""

import tempfile
from pathlib import Path

import pytest
from typer import Exit
from typer.testing import CliRunner

from xplat import constants
from xplat.cli import app, print_files, print_selected_info, rename_list
from xplat.list import validate_extension

_runner = CliRunner()


def test_app():
    """
    Runs a test case on the `app` function by invoking it
    and checking the result.

    Parameters:
    None

    Returns:
    None
    """
    result = _runner.invoke(app)
    assert result.exit_code == constants.MISSING_COMMAND
    # With newer Typer versions, error message appears in stderr
    assert "Missing command." in result.stderr or "Missing command." in result.stdout


def test_version():
    """
    Executes a unit test for both variants of the
    `app` command's version flag.

    Returns:
        None
    """
    result = _runner.invoke(app, ["--version"])
    assert result.exit_code == constants.NO_ERROR
    assert f"xplat version: {constants.VERSION}" in result.stdout

    result = _runner.invoke(app, ["-V"])
    assert result.exit_code == constants.NO_ERROR
    assert f"xplat version: {constants.VERSION}" in result.stdout


def test_info():
    """
    Executes the `info` command of the `app` module
    using `_runner` and asserts that the exit code
    is `constants.NO_ERROR`.
    Also asserts that "System Information" is present
    in the `stdout` of the `result`.

    This function does not take any parameters and does not return anything.
    """
    result = _runner.invoke(app, "info")
    assert result.exit_code == constants.NO_ERROR
    assert "System Information" in result.stdout


def test_list():
    """
    Runs a series of tests for the 'list' command. This includes checking if
    the command works with a required argument, lists files in a given
    directory, lists files in a given directory with a specific extension,
    retrieves information about a single file, removes test files and
    directories, and checks for non-existent directories.

    Args:
    None

    Returns:
    None
    """
    test_path = Path.home().joinpath("tmp", "xplat_cli_tests")
    test_path.mkdir(parents=True, exist_ok=True)
    # create a large file (20K) to test file size
    list_file_1 = test_path.joinpath("list_file_1.txt")
    list_file_1.touch(exist_ok=True)
    with list_file_1.open("w") as f:
        f.write("0123456789" * 2048)
    list_file_2 = test_path.joinpath("list_file_2.txt")
    list_file_2.touch(exist_ok=True)
    list_file_3 = test_path.joinpath("list_file_3.txt")
    list_file_3.touch(exist_ok=True)
    # check for required argument
    test_required_arg = _runner.invoke(app, "list", input="q\n")
    assert test_required_arg.exit_code == 0
    assert "Total files found =" in test_required_arg.stdout
    # list files in test directory.
    test_list_dir = _runner.invoke(app, ["list", str(test_path)], input="q\n")
    assert test_list_dir.exit_code == 0
    assert list_file_3.name in test_list_dir.stdout
    assert "Total files found = 3" in test_list_dir.stdout
    # list files in test directory with 'txt' extension
    test_ext = _runner.invoke(app, ["list", str(test_path), "--ext", "txt"], input="q\n")
    assert test_ext.exit_code == 0
    assert list_file_2.name in test_ext.stdout
    assert "Total files found = 3" in test_ext.stdout
    # list info for a single file
    test_file = _runner.invoke(app, ["list", str(list_file_1)], input="q\n")
    assert test_file.exit_code == 0
    assert list_file_1.name in test_file.stdout
    assert "Size:     20.0 K" in test_file.stdout
    # remove test files from test dir
    for file in test_path.iterdir():
        file.unlink()
    # remove test dir
    test_path.rmdir()
    # attempt to list files in non-existent directory
    test_list_dir = _runner.invoke(app, ["list", str(test_path)], input="q\n")
    assert test_list_dir.exit_code == constants.NO_FILE
    # check for non-existent directory
    # assert check_dir(test_path, "Test") is False


def test_print_files():
    # test for empty list
    test_empty = []
    list_count = print_files(test_empty)
    assert list_count == 0


def test_rename_list():
    """Test the rename_list function with various modes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Test dry-run mode first (web style default: hyphens)
        file_names = ["file with spaces.txt", "file#with#special#chars!.txt"]
        test_files = []
        for name in file_names:
            file_path = temp_dir / name
            file_path.write_text("test content")
            test_files.append(file_path)

        convert_count = rename_list(test_files, output_dir, dryrun=True)
        assert convert_count == 2
        # Original files should still exist
        for file_path in test_files:
            assert file_path.exists()
        # Output files should not exist (web style: hyphens)
        assert not (output_dir / "file-with-spaces.txt").exists()
        assert not (output_dir / "filewithspecialchars.txt").exists()

        # Now test non-interactive mode
        convert_count = rename_list(test_files, output_dir)
        assert convert_count == 2
        # Check renamed files exist (web style: hyphens)
        assert (output_dir / "file-with-spaces.txt").exists()
        assert (output_dir / "filewithspecialchars.txt").exists()


def test_rename_command():
    """Test the rename command with various options using positional source"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Create a test file
        test_file = temp_dir / "Test File.txt"
        test_file.write_text("test content")

        # Test dry run mode (positional source arg, web style default)
        result = runner.invoke(
            app,
            [
                "rename",
                str(temp_dir),
                "--output-dir",
                str(output_dir),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

        # Test non-interactive mode (default) — web style produces hyphens
        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir)],
        )
        assert result.exit_code == 0
        assert (output_dir / "test-file.txt").exists()

        # Test interactive mode with confirmation
        result = runner.invoke(
            app,
            [
                "rename",
                str(temp_dir),
                "--output-dir",
                str(output_dir),
                "--interactive",
            ],
            input="y\n",
        )
        assert result.exit_code == 0

        # Test interactive mode with cancellation
        result = runner.invoke(
            app,
            [
                "rename",
                str(temp_dir),
                "--output-dir",
                str(output_dir),
                "--interactive",
            ],
            input="n\n",
        )
        assert result.exit_code == 1


def test_print_selected_info(monkeypatch):
    # Sample files list
    files = ["file1.txt", "file2.txt", "file3.txt"]

    # Test for invalid input
    file_selector = "invalid"
    result = print_selected_info(files, file_selector)
    assert result == "Invalid input, please enter a number or 'q'.\n", "Incorrect error message for invalid input."

    # Test for out-of-range input
    file_selector = "5"
    result = print_selected_info(files, file_selector)
    expected_result = f"The number {file_selector} is out of range."
    assert expected_result in result, "Incorrect error message for out-of-range input."

    # The files in the files list are not real files
    # Test for non-existent path, user choosing to continue
    file_selector = "1"
    monkeypatch.setattr("typer.prompt", lambda _: "c")
    expected_result = "Select another file to examine.\n"
    result = print_selected_info(files, file_selector)
    assert expected_result in result, "Expected error message not found."
    # Test for non-existent path, user choosing to quit
    monkeypatch.setattr("typer.prompt", lambda _: "q")
    expected_error = "is not a path to a file."
    with pytest.raises(Exit):
        result = print_selected_info(files, file_selector)
        assert expected_error in result, "Expected error message not found."


# TDD Tests for --help functionality (these should FAIL with current Typer version)
def test_app_help():
    """
    Test that `xplat --help` works without crashing.
    This test should FAIL with current Typer 0.9.x due to compatibility issues.
    """
    result = _runner.invoke(app, ["--help"])
    assert result.exit_code == constants.NO_ERROR
    assert "Cross-platform tools for batch file management" in result.stdout
    assert "Commands:" in result.stdout or "Usage:" in result.stdout


def test_info_help():
    """
    Test that `xplat info --help` works without crashing.
    This test should FAIL with current Typer 0.9.x due to compatibility issues.
    """
    result = _runner.invoke(app, ["info", "--help"])
    assert result.exit_code == constants.NO_ERROR
    assert "info" in result.stdout.lower()


def test_list_help():
    """
    Test that `xplat list --help` works without crashing.
    This test should FAIL with current Typer 0.9.x due to compatibility issues.
    """
    result = _runner.invoke(app, ["list", "--help"])
    assert result.exit_code == constants.NO_ERROR
    assert "list" in result.stdout.lower()
    assert "--ext" in result.stdout or "extension" in result.stdout.lower()


def test_rename_help():
    """Test that `xplat rename --help` shows positional source and --style."""
    result = _runner.invoke(app, ["rename", "--help"])
    assert result.exit_code == constants.NO_ERROR
    assert "rename" in result.stdout.lower()
    assert "--style" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--interactive" in result.stdout


def test_help_flag_short():
    """Test that `xplat -h` works as a short form of --help."""
    result = _runner.invoke(app, ["-h"])
    assert result.exit_code == constants.NO_ERROR
    assert "Cross-platform tools for batch file management" in result.stdout


def test_validate_extension():
    """Test extension validation accepts valid and rejects invalid patterns."""
    # Valid extensions
    assert validate_extension("txt") == "txt"
    assert validate_extension(".pdf") == "pdf"
    assert validate_extension("JPG") == "JPG"
    assert validate_extension("mp3") == "mp3"

    # Invalid extensions with glob metacharacters
    with pytest.raises(ValueError, match="alphanumeric"):
        validate_extension("**/*")
    with pytest.raises(ValueError, match="alphanumeric"):
        validate_extension("*")
    with pytest.raises(ValueError, match="alphanumeric"):
        validate_extension("../../etc")
    with pytest.raises(ValueError, match="alphanumeric"):
        validate_extension("txt;rm -rf")


def test_rename_rejects_invalid_extension():
    """Test that rename command rejects invalid extension input."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(
            app,
            ["rename", temp_dir, "--ext", "**/*", "--dry-run"],
        )
        assert result.exit_code == 1


def test_version_from_metadata():
    """Test that version is loaded from package metadata."""
    assert constants.VERSION == "0.2.0"
    assert isinstance(constants.VERSION, str)
    assert constants.VERSION != "0.0.0-dev"


def test_rename_nonexistent_source():
    """Test that rename rejects a non-existent source path."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["rename", "/nonexistent/path", "--dry-run"],
    )
    assert result.exit_code == 1
    assert "does not exist" in result.stdout


def test_rename_nonexistent_output_dir():
    """Test that rename rejects a non-existent output directory."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(
            app,
            ["rename", temp_dir, "--output-dir", "/nonexistent/output"],
        )
        assert result.exit_code == 1
        assert "does not exist" in result.stdout


def test_rename_dry_run_no_output_dir():
    """Test dry-run rename without an output directory (in-place preview)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_file = temp_dir / "My Test File.txt"
        test_file.write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "renamed in place" in result.stdout


def test_rename_with_extension_filter():
    """Test rename filters files by extension."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Create files with different extensions
        (temp_dir / "Keep This.txt").write_text("txt")
        (temp_dir / "Skip This.pdf").write_text("pdf")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir), "--ext", "txt"],
        )
        assert result.exit_code == 0
        # Web style: hyphens
        assert (output_dir / "keep-this.txt").exists()
        assert not (output_dir / "skip-this.pdf").exists()


def test_rename_collision_skips_gracefully():
    """Test that rename skips files when target already exists."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Create source file and pre-existing target (web style: hyphens)
        (temp_dir / "Test File.txt").write_text("source")
        (output_dir / "test-file.txt").write_text("existing")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir)],
        )
        assert result.exit_code == 0
        assert "Skipped" in result.stdout
        # Original target content preserved
        assert (output_dir / "test-file.txt").read_text() == "existing"


def test_rename_interactive_abort_no_output_dir():
    """Test interactive mode abort when no output directory specified."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        (temp_dir / "File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--interactive"],
            input="n\n",
        )
        assert result.exit_code == 1


# --- New tests: positional source argument ---


def test_rename_positional_dir():
    """Test rename with positional directory argument."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        (temp_dir / "Test File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "test-file" in result.stdout


def test_rename_positional_file():
    """Test rename with positional single file argument."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_file = temp_dir / "My Screenshot.png"
        test_file.write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(test_file), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "my-screenshot" in result.stdout


def test_rename_default_cwd():
    """Test rename with no source argument defaults to cwd."""
    runner = CliRunner()
    # Invoke without source arg — should not crash (may find no files in cwd)
    result = runner.invoke(app, ["rename", "--dry-run"])
    assert result.exit_code == 0


# --- New tests: --style flag ---


def test_rename_style_snake():
    """Test rename with --style snake."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (temp_dir / "Test File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir), "--style", "snake"],
        )
        assert result.exit_code == 0
        assert (output_dir / "test_file.txt").exists()


def test_rename_style_kebab():
    """Test rename with --style kebab."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (temp_dir / "Test_File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir), "--style", "kebab"],
        )
        assert result.exit_code == 0
        assert (output_dir / "test-file.txt").exists()


def test_rename_style_camel():
    """Test rename with --style camel."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (temp_dir / "Test File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir), "--style", "camel"],
        )
        assert result.exit_code == 0
        assert (output_dir / "testFile.txt").exists()


def test_rename_style_web_default():
    """Test that no --style flag defaults to web (hyphens)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (temp_dir / "Test File.txt").write_text("content")

        result = runner.invoke(
            app,
            ["rename", str(temp_dir), "--output-dir", str(output_dir)],
        )
        assert result.exit_code == 0
        assert (output_dir / "test-file.txt").exists()


def test_rename_help_shows_style():
    """Test that --style appears in rename help output."""
    result = _runner.invoke(app, ["rename", "--help"])
    assert result.exit_code == 0
    assert "--style" in result.stdout
