"""The Command Line Interface (CLI) code for xplat
Uses the typer package to implement sub-commands, command options
and help text.
Only CLI code should be in this module, input and output for the user.
TODO: add logging, verbosity
"""

from pathlib import Path
from typing import Annotated

import typer

from xplat import constants
from xplat.info import create_platform_report
from xplat.list import FileInfo, check_file, create_file_list, validate_extension
from xplat.rename import Style, rename_file

# numeric constants
PROGRAM_NAME = constants.PROGRAM_NAME
VERSION = constants.VERSION
APP_HELP = constants.APP_HELP
NO_ERROR = constants.NO_ERROR
NO_FILE = constants.NO_FILE


def version_callback(is_version_requested: bool) -> None:
    """Display the version number and exit"""
    if is_version_requested:
        typer.echo(f"{PROGRAM_NAME} version: {VERSION}")
        raise typer.Exit(code=NO_ERROR)


def print_error(msg: str) -> None:
    """
    Display an error message
    """
    typer.secho(
        msg,
        fg=typer.colors.BRIGHT_WHITE,
        bg=typer.colors.RED,
    )


def print_header(ext: str | None) -> None:
    """
    Print a header for the file list
    """
    list_label = f"Listing files with extension '.{ext}':" if ext is not None else "Listing all files (no directories):"

    label_border = "-" * len(list_label)
    typer.echo(label_border)
    typer.secho(
        list_label,
        fg=typer.colors.BRIGHT_YELLOW,
    )
    typer.echo(label_border)


def print_files(files: list) -> int:
    """
    Print a list of files,
    return the number of files found
    """
    # sourcery skip: simplify-empty-collection-comparison
    # testing for the empty list works reliably, unlike boolean test
    if files == []:
        file_count = 0
    else:
        for file_count, file_name in enumerate(files, start=1):
            typer.secho(f"{file_count}) {Path(file_name).name}", fg=typer.colors.GREEN)

    # report the number of files found.
    file_report = f"Total files found = {file_count}"
    typer.echo("-" * len(file_report))
    typer.secho(file_report, fg=typer.colors.BRIGHT_YELLOW)

    return file_count


def print_file_data(file_info: FileInfo) -> None:
    """
    Print file properties in indented table format
    """
    typer.secho(f"{file_info.file_name}", fg=typer.colors.BRIGHT_GREEN)
    typer.echo(f"  Size:     {file_info.size}")
    typer.echo(f"  Created:  {file_info.created}")
    typer.echo(f"  Modified: {file_info.modified}")
    typer.echo(f"  Accessed: {file_info.accessed}")


def print_file_info(file_name: Path) -> None:
    """
    Display file information for a file
    """
    check_file_result = check_file(file_name)
    if check_file_result[0]:
        print_file_data(FileInfo(file_name))
    else:
        print_error(check_file_result[1])


def print_selected_info(files: list, selected: str) -> str:
    """
    Display file information for a selected file.

    Args:
        files (list): list of files to display
        selected (str): selected file number

    Returns:
        str: prompt to display, depending on input
    """

    # input should be an integer
    try:
        file_index = int(selected) - 1
    except ValueError:
        return "Invalid input, please enter a number or 'q'.\n"

    # is the number valid?
    if file_index < 0 or file_index > len(files) - 1:
        message = f"The number {selected} is out of range.\n"
        message += f"Please enter a number between 1 and {len(files)}.\n"
        return message

    print_file_info(files[file_index])

    # prompt to continue
    user_input = typer.prompt("Enter 'q' to quit, 'c' to continue")
    if user_input == "q":
        raise typer.Exit(code=NO_ERROR)

    # continue with default prompt
    return "Select another file to examine.\n"


def review_files(directory: Path, extension: str | None = None) -> None:
    """
    Displays a list of files and prompts for file selection
    """
    files = create_file_list(directory, extension)
    basic_prompt = "Enter a number to show file info, or 'q' to quit"
    full_prompt = basic_prompt

    # repeat until the user quits
    while True:
        print_header(extension)
        print_files(files)

        file_selector = typer.prompt(full_prompt)

        if file_selector == "q":
            break

        full_prompt = print_selected_info(files, file_selector) + basic_prompt


def rename_file_with_output(
    file_name: Path,
    output_dir: Path | None = None,
    dry_run: bool = False,
    label: str = "",
    style: Style = Style.web,
) -> None:
    """
    Renames a file with the given name to a new name
    and outputs both names.
    """
    typer.echo(label)
    typer.secho(f"Original: {file_name}", fg=typer.colors.CYAN)
    typer.echo("  to:")
    new_path = rename_file(file_name, output_dir, dry_run, style)
    typer.secho(f"     New: {new_path}", fg=typer.colors.BRIGHT_CYAN)
    typer.echo("")


def rename_list(
    files: list,
    output_dir: Path | None = None,
    dryrun: bool = False,
    style: Style = Style.web,
) -> int:
    """
    Rename files in list, optionally to output directory
    """
    if dryrun:
        typer.secho("DRY RUN - No files will be changed", fg=typer.colors.YELLOW)
        typer.echo("")
        start_label = "Proposed rename:"
    else:
        start_label = "Converting file name:"

    skip_count = 0
    for current_name in files:
        try:
            rename_file_with_output(current_name, output_dir, dryrun, start_label, style)
        except (FileExistsError, OSError, ValueError) as e:
            print_error(f"Skipped: {e}")
            skip_count += 1

    convert_count = len(files) - skip_count

    if dryrun:
        typer.echo("")
        typer.secho(f"Found {convert_count} files to rename", fg=typer.colors.GREEN)
        if output_dir:
            typer.echo(f"Files would be renamed and saved to: {output_dir}")
        else:
            typer.echo("Files would be renamed in place")

    return convert_count


# CLI interface
# sourcery skip: avoid-global-variables
# module level variables are required by typer
app = typer.Typer(
    help=constants.APP_HELP,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            help="Print the version number.",
        ),
    ] = None,
) -> None:
    """Empty function required for version callback"""
    pass


@app.command()
def info() -> None:
    """Display platform information."""
    typer.echo(create_platform_report())


@app.command(name="list")
def list_files(
    path: Annotated[Path | None, typer.Argument(help="Path to file or directory")] = None,
    ext: Annotated[str | None, typer.Option("--ext", "-x", help="File extension filter")] = None,
) -> None:
    """
    List files in a directory, or info for a file
    """
    error_code = NO_FILE
    if path is None:
        path = Path.cwd()
    if path.is_file():
        # list file information for a single file
        print_file_info(path)
    elif path.is_dir():
        review_files(path, ext)
    else:
        raise typer.Exit(code=error_code)


@app.command()
def rename(
    source: Annotated[Path | None, typer.Argument(help="File or directory to rename (default: current directory)")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir", "-o", help="Output directory")] = None,
    ext: Annotated[str | None, typer.Option("--ext", "-e", help="File extension filter")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n", help="Preview changes without modifying")] = False,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Interactive confirmation mode")] = False,
    style: Annotated[Style, typer.Option("--style", help="Naming style: web, snake, kebab, camel")] = Style.web,
) -> None:
    """Convert file names for cross-platform compatibility"""
    # Default to current directory if no source given
    if source is None:
        source = Path.cwd()

    # Check source exists
    if not source.exists():
        typer.secho(
            f"Source {source} does not exist.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # check output dir exists if specified
    if output_dir is not None and not output_dir.exists():
        typer.secho(
            f"Output directory {output_dir} does not exist.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # validate extension if specified
    if ext is not None:
        try:
            ext = validate_extension(ext)
        except ValueError as e:
            typer.secho(str(e), fg=typer.colors.RED)
            raise typer.Exit(1) from e

    # Single file mode
    if source.is_file():
        rename_list([source], output_dir, dry_run, style)
        return

    # Directory mode: collect matching files
    files = [
        item for item in source.iterdir()
        if item.is_file() and (ext is None or item.suffix == f".{ext}")
    ]

    # Only show file listing if in interactive mode or dry run
    if interactive and not dry_run:
        for count, file in enumerate(files, start=1):
            typer.echo(f"{count}) {file.name}")
        typer.echo("----------------------")
        typer.echo(f"Total files found = {len(files)}")

        if output_dir is not None:
            typer.echo("Selected files will be renamed and saved to:")
            typer.echo(f"{output_dir}")
            if not typer.confirm(f"Rename {len(files)} files of type '{ext}'?"):
                raise typer.Abort()
        else:
            if not typer.confirm("No output directory specified. Rename files?"):
                raise typer.Abort()

    rename_list(files, output_dir, dry_run, style)


if __name__ == "__main__":
    app()
