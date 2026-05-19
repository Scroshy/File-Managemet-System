from pathlib import Path
from typing import Union

from basic import copy_file, unique_destination
from flattener import FLATTEN_SEPARATOR


def _unescape_part(part: str) -> str:
    """Restore a path component encoded by the flattener."""
    doubled = FLATTEN_SEPARATOR * 2
    return part.replace(doubled, FLATTEN_SEPARATOR)


def parse_flat_filename(filename: str) -> Path | None:
    """
    Decode a flattened filename back into a relative path.

    Example: my_files__FLAT__personal__FLAT__secret.txt
    -> my_files/personal/secret.txt
    """
    sep = FLATTEN_SEPARATOR
    doubled = sep * 2
    parts: list[str] = []
    current: list[str] = []
    i = 0

    while i < len(filename):
        if filename.startswith(doubled, i):
            current.append(sep)
            i += len(doubled)
        elif filename.startswith(sep, i):
            parts.append(_unescape_part("".join(current)))
            current = []
            i += len(sep)
        else:
            current.append(filename[i])
            i += 1

    parts.append(_unescape_part("".join(current)))

    if len(parts) < 2:
        return None

    return Path(*parts)


def unflatten_folder(
    flattened_directory: Union[str, Path],
    output_root: Union[str, Path, None] = None,
) -> bool:
    """
    Restore files from a flattened folder back into nested directories.

    Filenames must have been produced by flatten_folder (see flattener.py).
    By default, files are recreated next to the flattened folder (its parent).

    Args:
        flattened_directory: Folder containing flattened files
        output_root: Where to recreate the tree (defaults to flattened folder's parent)

    Returns:
        True if all copies succeeded (or there were no valid files), False otherwise
    """
    try:
        flattened_directory = Path(flattened_directory).resolve()

        if not flattened_directory.exists():
            print(f"Error: Directory '{flattened_directory}' does not exist.")
            return False

        if not flattened_directory.is_dir():
            print(f"Error: '{flattened_directory}' is not a directory.")
            return False

        if output_root is None:
            output_root = flattened_directory.parent
        else:
            output_root = Path(output_root).resolve()

        files = [path for path in flattened_directory.iterdir() if path.is_file()]
        if not files:
            print(f"No files to unflatten in '{flattened_directory}'.")
            return True

        success = True
        restored = 0
        skipped = 0

        for file_path in files:
            relative_path = parse_flat_filename(file_path.name)
            if relative_path is None:
                print(f"Skipping (not a flattened name): '{file_path.name}'")
                skipped += 1
                continue

            destination = output_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            final_path = unique_destination(destination.parent, destination.name)

            if not copy_file(file_path, final_path):
                success = False
            else:
                restored += 1

        if success and restored:
            print(
                f"Restored {restored} file(s) from '{flattened_directory}' "
                f"under '{output_root}'."
            )
        elif success and skipped and not restored:
            print("No flattened files found to restore.")
        elif skipped:
            print(f"Skipped {skipped} file(s) with unrecognized names.")

        return success

    except Exception as e:
        print(f"Error unflattening folder: {e}")
        return False
