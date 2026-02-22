"""
Functions for transforming filenames to be platform and web-friendly.
Handles conversion of spaces, dots, and case in filenames.

Supports multiple naming styles:
* web (default): lowercase, hyphens — URL-safe
* snake: lowercase, underscores — Python/filesystem-friendly
* kebab: lowercase, hyphens — same as web but converts underscores
* camel: camelCase — no separators

Characters allowed in a URL:
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789
Special characters:
safe  $-_.+
reserved  ;/?:@&=
extra  ,[]
https://www.rfc-editor.org/rfc/rfc3986
or
https://www.ietf.org/rfc/rfc1738.txt
"""

import re
from enum import Enum
from pathlib import Path


class Style(str, Enum):
    """Naming style for safe filenames."""

    web = "web"
    snake = "snake"
    kebab = "kebab"
    camel = "camel"


def _normalize_whitespace(name: str) -> str:
    """Normalize all Unicode whitespace to ASCII space, then strip."""
    return re.sub(r"\s", " ", name).strip()


def _apply_delimiter_style(name: str, delim: str, convert_chars: str) -> str:
    """Apply a delimiter-based style: replace chars, filter, collapse, strip.

    Args:
        name: Pre-normalized filename stem
        delim: The delimiter character ("-" or "_")
        convert_chars: Characters to convert to the delimiter (e.g., " ._" or " .-")
    """
    result = name.lower()
    for ch in convert_chars:
        result = result.replace(ch, delim)
    # Keep only alphanumeric + delimiter (web also keeps underscores via allowed_extra)
    allowed = {delim} | ({"_"} if delim == "-" and "_" not in convert_chars else set())
    result = "".join(c for c in result if c.isalnum() or c in allowed)
    double = delim + delim
    while double in result:
        result = result.replace(double, delim)
    return result.strip(delim)


def _apply_camel(name: str) -> str:
    """Camel style: remove separators, produce camelCase."""
    parts = re.split(r"[ .\-_]+", name)
    clean_parts = [
        cleaned
        for part in parts
        if (cleaned := "".join(c for c in part if c.isalnum()))
    ]
    if not clean_parts:
        return ""
    return clean_parts[0].lower() + "".join(p.title() for p in clean_parts[1:])


# Style config: (delimiter, characters to convert to delimiter)
_STYLE_CONFIG: dict[Style, tuple[str, str]] = {
    Style.web: ("-", " ."),       # keep hyphens, keep underscores
    Style.snake: ("_", " .-"),    # convert everything to underscore
    Style.kebab: ("-", " ._"),    # convert everything to hyphen
}


def safe_stem(name: str, style: Style = Style.web) -> str:
    """Transform a filename stem to be platform and web-friendly.

    Args:
        name: Original filename stem
        style: Naming style (default: web)

    Returns:
        Transformed filename stem using the specified style.
    """
    normalized = _normalize_whitespace(name)
    if not normalized:
        return ""
    if style == Style.camel:
        return _apply_camel(normalized)
    delim, convert_chars = _STYLE_CONFIG[style]
    return _apply_delimiter_style(normalized, delim, convert_chars)


def make_safe_path(
    orig_path: Path,
    target_dir: Path | None = None,
    style: Style = Style.web,
) -> Path:
    """Create a new Path with safe filename in target directory.

    Args:
        orig_path: Original file path
        target_dir: Optional target directory for new path
        style: Naming style (default: web)

    Returns:
        New Path with safe filename in original or target directory
    """
    stem = safe_stem(orig_path.stem, style)
    if not stem:
        raise ValueError(f"Filename produces empty stem after sanitization: {orig_path.name}")
    new_name = stem + orig_path.suffix.lower()
    return target_dir.joinpath(new_name) if target_dir else orig_path.with_name(new_name)


def rename_file(
    orig_path: Path,
    target_dir: Path | None = None,
    dry_run: bool = False,
    style: Style = Style.web,
) -> Path:
    """Rename file to be platform and web-friendly.

    Args:
        orig_path: Path to original file
        target_dir: Optional target directory for renamed file
        dry_run: If True, only return the new path without performing rename
        style: Naming style (default: web)

    Returns:
        Path to renamed file (or would-be path if dry_run=True)

    Raises:
        FileNotFoundError: If original path is not a file
        NotADirectoryError: If target directory is specified but invalid
        FileExistsError: If target path already exists (unless dry_run=True)
        OSError: If original path is a symlink
    """
    if orig_path.is_symlink():
        raise OSError(f"Refusing to operate on symlink: {orig_path}")
    if not orig_path.is_file():
        raise FileNotFoundError(f"Not a file: {orig_path}")
    if target_dir and not target_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {target_dir}")

    new_path = make_safe_path(orig_path, target_dir, style)

    if not dry_run and new_path.exists():
        raise FileExistsError(f"File already exists: {new_path}")

    if not dry_run:
        orig_path.rename(new_path)

    return new_path
