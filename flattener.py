from pathlib import Path
from typing import Union

from app_io import debug, error, get_logger, info, success, warning
from basic import copy_file, unique_destination
from constants import FLATTEN_OUTPUT_SUFFIX, FLATTEN_SEPARATOR

logger = get_logger("flattener")


def _escape_part(part: str) -> str:
    """Escape separator characters inside a single path component."""
    doubled = FLATTEN_SEPARATOR * 2
    return part.replace(FLATTEN_SEPARATOR, doubled)


def _flattened_output_dir(source: Path) -> Path:
    """Return a sibling folder name like my_files_flattened or my_files_flattened_1."""
    suffix = FLATTEN_OUTPUT_SUFFIX
    candidate = source.parent / f"{source.name}{suffix}"
    if not candidate.exists():
        return candidate

    counter = 1
    while True:
        candidate = source.parent / f"{source.name}{suffix}_{counter}"
        if not candidate.exists():
            return candidate
        counter += 1


def _flattened_filename(source_root: Path, file_path: Path) -> str:
    """
    Build a flat filename from the file's path under source_root.

    Example: source_root=my_files, file=my_files/personal/secret.txt
    -> my_files__FLAT__personal__FLAT__secret.txt
    """
    relative = file_path.relative_to(source_root)
    parts = (source_root.name,) + relative.parts
    return FLATTEN_SEPARATOR.join(_escape_part(part) for part in parts)


def flatten_folder(directory: Union[str, Path]) -> bool:
    """
    Recursively collect all files under directory and copy them into a single
    sibling folder named {folder_name}<flatten_output_suffix> (with a numeric suffix if needed).

    Original files and folder structure are left unchanged.

    Each copy is renamed using its path relative to the source folder, with
    FLATTEN_SEPARATOR between components (including the source folder name).

    Args:
        directory: Root folder to flatten

    Returns:
        True if all copies succeeded (or there were no files), False otherwise
    """
    try:
        directory = Path(directory).resolve()
        logger.info("flatten_folder started: %s", directory)

        if not directory.exists():
            error(f"Directory '{directory}' does not exist.", logger=logger)
            return False

        if not directory.is_dir():
            error(f"'{directory}' is not a directory.", logger=logger)
            return False

        files = [path for path in directory.rglob("*") if path.is_file()]
        if not files:
            info(f"No files to flatten in '{directory}'.", logger=logger)
            return True

        output_dir = _flattened_output_dir(directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Flatten output directory: %s", output_dir)

        success_count = 0
        operation_ok = True
        for file_path in files:
            flat_name = _flattened_filename(directory, file_path)
            destination = unique_destination(output_dir, flat_name)
            debug(f"Flattening '{file_path}' as '{destination.name}'", logger=logger)
            if copy_file(file_path, destination):
                success_count += 1
            else:
                operation_ok = False

        if operation_ok:
            success(
                f"Flattened {success_count} file(s) from '{directory}' into '{output_dir}'.",
                logger=logger,
            )
        else:
            warning(
                f"Flatten completed with errors ({success_count}/{len(files)} files).",
                logger=logger,
            )
        return operation_ok

    except Exception as exc:
        error(f"Error flattening folder: {exc}", logger=logger)
        logger.exception("flatten_folder failed")
        return False
