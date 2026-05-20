from pathlib import Path
from typing import Union

from app_io import debug, error, get_logger, info, success, warning
from basic import move_file, unique_destination

logger = get_logger("sort_by_extension")


def _extension_folder_name(file_path: Path) -> str:
    """Return a folder name for the file's extension (e.g. 'pdf' for .pdf)."""
    suffix = file_path.suffix.lower()
    if suffix:
        return suffix.lstrip(".")
    return "no_extension"


def sort_by_extension(directory: Union[str, Path]) -> bool:
    """
    Sort files in a directory into subfolders named by their extension.

    For example, report.pdf and notes.txt in ./Downloads become
    ./Downloads/pdf/report.pdf and ./Downloads/txt/notes.txt.

    Args:
        directory: Path to the folder whose files should be sorted

    Returns:
        True if all moves succeeded (or there was nothing to sort), False otherwise
    """
    try:
        directory = Path(directory)
        logger.info("sort_by_extension started: %s", directory)

        if not directory.exists():
            error(f"Directory '{directory}' does not exist.", logger=logger)
            return False

        if not directory.is_dir():
            error(f"'{directory}' is not a directory.", logger=logger)
            return False

        files = [path for path in directory.iterdir() if path.is_file()]
        if not files:
            info(f"No files to sort in '{directory}'.", logger=logger)
            return True

        success_count = 0
        operation_ok = True
        for file_path in files:
            ext_folder = directory / _extension_folder_name(file_path)
            ext_folder.mkdir(exist_ok=True)
            destination = unique_destination(ext_folder, file_path.name)
            debug(f"Sorting '{file_path.name}' -> '{destination}'", logger=logger)
            if move_file(file_path, destination):
                success_count += 1
            else:
                operation_ok = False

        if operation_ok:
            success(
                f"Sorted {success_count} file(s) by extension in '{directory}'.",
                logger=logger,
            )
        else:
            warning(
                f"Sort completed with errors ({success_count}/{len(files)} files).",
                logger=logger,
            )
        return operation_ok

    except Exception as exc:
        error(f"Error sorting files by extension: {exc}", logger=logger)
        logger.exception("sort_by_extension failed")
        return False
