import shutil
from pathlib import Path
from typing import Union

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None


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
        
        if not source.exists():
            print(f"Error: Source file '{source}' does not exist.")
            return False
        
        if not source.is_file():
            print(f"Error: '{source}' is not a file.")
            return False
        
        # Create destination directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source, destination)
        print(f"File copied successfully: '{source}' -> '{destination}'")
        return True
    
    except Exception as e:
        print(f"Error copying file: {e}")
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
        
        if not source.exists():
            print(f"Error: Source folder '{source}' does not exist.")
            return False
        
        if not source.is_dir():
            print(f"Error: '{source}' is not a directory.")
            return False
        
        # Create parent directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"Folder copied successfully: '{source}' -> '{destination}'")
        return True
    
    except Exception as e:
        print(f"Error copying folder: {e}")
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
        
        if not source.exists():
            print(f"Error: Source file '{source}' does not exist.")
            return False
        
        if not source.is_file():
            print(f"Error: '{source}' is not a file.")
            return False
        
        # Create destination directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source), str(destination))
        print(f"File moved successfully: '{source}' -> '{destination}'")
        return True
    
    except Exception as e:
        print(f"Error moving file: {e}")
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
        
        if not source.exists():
            print(f"Error: Source folder '{source}' does not exist.")
            return False
        
        if not source.is_dir():
            print(f"Error: '{source}' is not a directory.")
            return False
        
        # Create parent directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source), str(destination))
        print(f"Folder moved successfully: '{source}' -> '{destination}'")
        return True
    
    except Exception as e:
        print(f"Error moving folder: {e}")
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
        
        if not path.exists():
            print(f"Error: Path '{path}' does not exist.")
            return False
        
        if send2trash is not None:
            # Use send2trash for proper recycle bin functionality
            send2trash(str(path))
            print(f"Item sent to recycle bin: '{path}'")
        else:
            # Fallback: move to "Deleted" folder for safety
            deleted_folder = Path.cwd() / "Deleted"
            deleted_folder.mkdir(exist_ok=True)
            
            destination = deleted_folder / path.name
            shutil.move(str(path), str(destination))
            print(f"Item moved to 'Deleted' folder: '{path}' -> '{destination}'")
        
        return True
    
    except Exception as e:
        print(f"Error deleting item: {e}")
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
        
        if not path.exists():
            print(f"Error: File '{path}' does not exist.")
            return False
        
        if not path.is_file():
            print(f"Error: '{path}' is not a file.")
            return False
        
        new_path = path.parent / new_name
        path.rename(new_path)
        print(f"File renamed successfully: '{path.name}' -> '{new_name}'")
        return True
    
    except Exception as e:
        print(f"Error renaming file: {e}")
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
        
        if not path.exists():
            print(f"Error: Folder '{path}' does not exist.")
            return False
        
        if not path.is_dir():
            print(f"Error: '{path}' is not a directory.")
            return False
        
        new_path = path.parent / new_name
        path.rename(new_path)
        print(f"Folder renamed successfully: '{path.name}' -> '{new_name}'")
        return True
    
    except Exception as e:
        print(f"Error renaming folder: {e}")
        return False
