from pathlib import Path
from typing import Union

from app_io import debug, get_logger

logger = get_logger("folder_compare")


def _relative_file_paths(folder: Path, *, recursive: bool) -> set[str]:
    """Collect file paths relative to folder (root folder name is not included)."""
    folder = folder.resolve()
    if recursive:
        return {
            path.relative_to(folder).as_posix()
            for path in folder.rglob("*")
            if path.is_file()
        }
    return {path.name for path in folder.iterdir() if path.is_file()}


def compare_folder_filenames(
    folder_a: Union[str, Path],
    folder_b: Union[str, Path],
    *,
    recursive: bool = True,
) -> bool:
    """
    Check whether two folders contain the same file paths relative to each root.

    Folder names themselves are ignored; only relative paths and file names matter.
    For example, folder_a/docs/readme.txt and folder_b/docs/readme.txt match.

    Args:
        folder_a: First folder to compare
        folder_b: Second folder to compare
        recursive: If True, include files in subfolders; if False, only top-level files

    Returns:
        True if both folders have exactly the same relative file paths
    """
    match, _, _ = compare_folder_filenames_report(
        folder_a, folder_b, recursive=recursive
    )
    return match


def compare_folder_filenames_report(
    folder_a: Union[str, Path],
    folder_b: Union[str, Path],
    *,
    recursive: bool = True,
) -> tuple[bool, set[str], set[str]]:
    """
    Compare two folders and report paths only in one or the other.

    Returns:
        (is_match, only_in_a, only_in_b) — paths use forward slashes
    """
    folder_a = Path(folder_a).resolve()
    folder_b = Path(folder_b).resolve()
    logger.info(
        "compare_folder_filenames_report: %s vs %s (recursive=%s)",
        folder_a,
        folder_b,
        recursive,
    )

    if not folder_a.is_dir():
        logger.error("'%s' is not a directory.", folder_a)
        raise NotADirectoryError(f"'{folder_a}' is not a directory.")
    if not folder_b.is_dir():
        logger.error("'%s' is not a directory.", folder_b)
        raise NotADirectoryError(f"'{folder_b}' is not a directory.")

    paths_a = _relative_file_paths(folder_a, recursive=recursive)
    paths_b = _relative_file_paths(folder_b, recursive=recursive)
    debug(f"Folder A file count: {len(paths_a)}", logger=logger)
    debug(f"Folder B file count: {len(paths_b)}", logger=logger)

    only_in_a = paths_a - paths_b
    only_in_b = paths_b - paths_a
    is_match = not only_in_a and not only_in_b
    logger.info(
        "Compare result: match=%s, only_in_a=%d, only_in_b=%d",
        is_match,
        len(only_in_a),
        len(only_in_b),
    )
    return (is_match, only_in_a, only_in_b)
