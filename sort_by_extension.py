from pathlib import Path
from typing import Union

from basic import move_file, unique_destination


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

        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist.")
            return False

        if not directory.is_dir():
            print(f"Error: '{directory}' is not a directory.")
            return False

        files = [path for path in directory.iterdir() if path.is_file()]
        if not files:
            print(f"No files to sort in '{directory}'.")
            return True

        success = True
        for file_path in files:
            ext_folder = directory / _extension_folder_name(file_path)
            ext_folder.mkdir(exist_ok=True)
            destination = unique_destination(ext_folder, file_path.name)
            if not move_file(file_path, destination):
                success = False

        if success:
            print(f"Sorted {len(files)} file(s) by extension in '{directory}'.")
        return success

    except Exception as e:
        print(f"Error sorting files by extension: {e}")
        return False
