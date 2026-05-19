from pathlib import Path
from typing import Union

from basic import copy_file, unique_destination

# Encodes nested paths in a single filename; unlikely in real path components.
FLATTEN_SEPARATOR = "__FLAT__"


def _escape_part(part: str) -> str:
    """Escape separator characters inside a single path component."""
    doubled = FLATTEN_SEPARATOR * 2
    return part.replace(FLATTEN_SEPARATOR, doubled)


def _flattened_output_dir(source: Path) -> Path:
    """Return a sibling folder name like my_files_flattened or my_files_flattened_1."""
    candidate = source.parent / f"{source.name}_flattened"
    if not candidate.exists():
        return candidate

    counter = 1
    while True:
        candidate = source.parent / f"{source.name}_flattened_{counter}"
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
    sibling folder named {folder_name}_flattened (with a numeric suffix if needed).

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

        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist.")
            return False

        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory.")
            return False

        files = [
            path
            for path in directory.rglob("*")
            if path.is_file()
        ]
        if not files:
            print(f"No files to flatten in '{directory}'.")
            return True

        output_dir = _flattened_output_dir(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        success = True
        for file_path in files:
            flat_name = _flattened_filename(directory, file_path)
            destination = unique_destination(output_dir, flat_name)
            if not copy_file(file_path, destination):
                success = False

        if success:
            print(
                f"Flattened {len(files)} file(s) from '{directory}' "
                f"into '{output_dir}'."
            )
        return success

    except Exception as e:
        print(f"Error flattening folder: {e}")
        return False
