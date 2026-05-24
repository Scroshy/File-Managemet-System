import shutil
from pathlib import Path
from typing import Union

from app_io import debug, error, get_logger, success

from constants import DELETE_FALLBACK_FOLDER

logger = get_logger("basic")

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None
    logger.warning("send2trash not installed; delete will use Deleted folder fallback")


def unique_destination(folder: Union[str, Path], filename: str) -> Path:
    """
    Return a file path in folder/filename that does not already exist.

    If filename is taken, appends _1, _2, ... before the extension.
    """
    folder = Path(folder)
    destination = folder / filename
    if not destination.exists():
        return destination

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            debug(
                f"Resolved name collision: '{filename}' -> '{candidate.name}'",
                logger=logger,
            )
            return candidate
        counter += 1


def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.

    Args:
        source: Path to the source file
        destination: Path to the destination file

    Returns:
        True if successful, False otherwise
    """
    try:
        source = Path(source)
        destination = Path(destination)
        logger.debug("copy_file: %s -> %s", source, destination)

        if not source.exists():
            error(f"Source file '{source}' does not exist.", logger=logger)
            return False

        if not source.is_file():
            error(f"'{source}' is not a file.", logger=logger)
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        success(f"File copied: '{source}' -> '{destination}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error copying file: {exc}", logger=logger)
        logger.exception("copy_file failed")
        return False


def copy_folder(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Copy a folder and all its contents from source to destination.

    Args:
        source: Path to the source folder
        destination: Path to the destination folder

    Returns:
        True if successful, False otherwise
    """
    try:
        source = Path(source)
        destination = Path(destination)
        logger.debug("copy_folder: %s -> %s", source, destination)

        if not source.exists():
            error(f"Source folder '{source}' does not exist.", logger=logger)
            return False

        if not source.is_dir():
            error(f"'{source}' is not a directory.", logger=logger)
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, dirs_exist_ok=True)
        success(f"Folder copied: '{source}' -> '{destination}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error copying folder: {exc}", logger=logger)
        logger.exception("copy_folder failed")
        return False


def move_file(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Move a file from source to destination.

    Args:
        source: Path to the source file
        destination: Path to the destination file

    Returns:
        True if successful, False otherwise
    """
    try:
        source = Path(source)
        destination = Path(destination)
        logger.debug("move_file: %s -> %s", source, destination)

        if not source.exists():
            error(f"Source file '{source}' does not exist.", logger=logger)
            return False

        if not source.is_file():
            error(f"'{source}' is not a file.", logger=logger)
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        success(f"File moved: '{source}' -> '{destination}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error moving file: {exc}", logger=logger)
        logger.exception("move_file failed")
        return False


def move_folder(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Move a folder and all its contents from source to destination.

    Args:
        source: Path to the source folder
        destination: Path to the destination folder

    Returns:
        True if successful, False otherwise
    """
    try:
        source = Path(source)
        destination = Path(destination)
        logger.debug("move_folder: %s -> %s", source, destination)

        if not source.exists():
            error(f"Source folder '{source}' does not exist.", logger=logger)
            return False

        if not source.is_dir():
            error(f"'{source}' is not a directory.", logger=logger)
            return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        success(f"Folder moved: '{source}' -> '{destination}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error moving folder: {exc}", logger=logger)
        logger.exception("move_folder failed")
        return False


def delete_to_recycle_bin(path: Union[str, Path]) -> bool:
    """
    Delete a file or folder and send it to the recycle bin (Windows).
    Uses send2trash library if available, otherwise moves to a "Deleted" folder.

    Args:
        path: Path to the file or folder to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(path)
        logger.debug("delete_to_recycle_bin: %s", path)

        if not path.exists():
            error(f"Path '{path}' does not exist.", logger=logger)
            return False

        if send2trash is not None:
            send2trash(str(path))
            success(f"Item sent to recycle bin: '{path}'", logger=logger)
        else:
            deleted_folder = Path.cwd() / DELETE_FALLBACK_FOLDER
            deleted_folder.mkdir(exist_ok=True)
            destination = deleted_folder / path.name
            shutil.move(str(path), str(destination))
            success(
                f"Item moved to 'Deleted' folder: '{path}' -> '{destination}'",
                logger=logger,
            )

        return True

    except Exception as exc:
        error(f"Error deleting item: {exc}", logger=logger)
        logger.exception("delete_to_recycle_bin failed")
        return False


def rename_file(path: Union[str, Path], new_name: str) -> bool:
    """
    Rename a file.

    Args:
        path: Path to the file
        new_name: New filename (can include subdirectory path)

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(path)
        logger.debug("rename_file: %s -> %s", path, new_name)

        if not path.exists():
            error(f"File '{path}' does not exist.", logger=logger)
            return False

        if not path.is_file():
            error(f"'{path}' is not a file.", logger=logger)
            return False

        new_path = path.parent / new_name
        path.rename(new_path)
        success(f"File renamed: '{path.name}' -> '{new_name}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error renaming file: {exc}", logger=logger)
        logger.exception("rename_file failed")
        return False


def rename_folder(path: Union[str, Path], new_name: str) -> bool:
    """
    Rename a folder.

    Args:
        path: Path to the folder
        new_name: New folder name

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(path)
        logger.debug("rename_folder: %s -> %s", path, new_name)

        if not path.exists():
            error(f"Folder '{path}' does not exist.", logger=logger)
            return False

        if not path.is_dir():
            error(f"'{path}' is not a directory.", logger=logger)
            return False

        new_path = path.parent / new_name
        path.rename(new_path)
        success(f"Folder renamed: '{path.name}' -> '{new_name}'", logger=logger)
        return True

    except Exception as exc:
        error(f"Error renaming folder: {exc}", logger=logger)
        logger.exception("rename_folder failed")
        return False
