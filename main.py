"""Console dashboard for the file management toolkit."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from app_io import (
    error,
    get_config,
    get_console,
    get_logger,
    info,
    setup,
    style,
    success,
    warning,
)
from basic import (
    copy_file,
    copy_folder,
    delete_to_recycle_bin,
    move_file,
    move_folder,
    rename_file,
    rename_folder,
)
from flattener import flatten_folder
from folder_compare import compare_folder_filenames_report
from sort_by_extension import sort_by_extension
from unflattener import unflatten_folder

logger = get_logger("main")
console = get_console()

MENU_ITEMS: list[tuple[str, str]] = [
    ("1", "Copy file"),
    ("2", "Copy folder"),
    ("3", "Move file"),
    ("4", "Move folder"),
    ("5", "Rename file"),
    ("6", "Rename folder"),
    ("7", "Delete to recycle bin"),
    ("8", "Sort files by extension"),
    ("9", "Flatten folder (nested → flat)"),
    ("10", "Unflatten folder (flat → nested)"),
    ("11", "Compare two folders (filenames)"),
]


def _tk_root() -> tk.Tk:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return root


def pick_file(title: str = "Select a file") -> Path | None:
    logger.debug("Opening file picker: %s", title)
    root = _tk_root()
    try:
        path = filedialog.askopenfilename(title=title)
    finally:
        root.destroy()
    if path:
        logger.info("File selected: %s", path)
        return Path(path)
    logger.info("File picker cancelled: %s", title)
    return None


def pick_folder(title: str = "Select a folder") -> Path | None:
    logger.debug("Opening folder picker: %s", title)
    root = _tk_root()
    try:
        path = filedialog.askdirectory(title=title)
    finally:
        root.destroy()
    if path:
        logger.info("Folder selected: %s", path)
        return Path(path)
    logger.info("Folder picker cancelled: %s", title)
    return None


def pick_save_file(
    title: str = "Choose destination",
    *,
    initialfile: str = "",
) -> Path | None:
    logger.debug("Opening save dialog: %s", title)
    root = _tk_root()
    try:
        path = filedialog.asksaveasfilename(
            title=title,
            initialfile=initialfile or None,
            defaultextension="",
        )
    finally:
        root.destroy()
    if path:
        logger.info("Save path selected: %s", path)
        return Path(path)
    logger.info("Save dialog cancelled: %s", title)
    return None


def _cancelled() -> None:
    warning("Selection cancelled.", logger=logger)


def _prompt_yes_no(question: str, *, default: bool = True) -> bool:
    result = Confirm.ask(
        f"[{style('accent')}]{question}[/]",
        default=default,
        console=console,
    )
    logger.debug("Prompt '%s' -> %s", question, result)
    return result


def _print_dashboard() -> None:
    config = get_config()
    title_text = config["app"]["title"]
    padding = tuple(config["rich"]["panel_padding"])

    title = Text(title_text, style=style("title"), justify="center")
    console.print(
        Panel(
            title,
            border_style=style("panel_border"),
            padding=padding,
            expand=False,
        )
    )

    table = Table(
        show_header=True,
        header_style=style("table_header"),
        border_style=style("table_border"),
        pad_edge=False,
        expand=False,
    )
    table.add_column("#", style=style("menu_key"), justify="right", width=4)
    table.add_column("Feature", style=style("menu_label"))
    for key, label in MENU_ITEMS:
        table.add_row(key, label)
    console.print(table)
    console.print(
        f"[{style('info')}]Enter a number to run a feature, or[/] "
        f"[{style('error')}]Q[/] [{style('info')}]to quit.[/]\n"
    )
    logger.debug("Dashboard rendered")


def _handle_copy_file() -> None:
    logger.info("Feature: copy file")
    source = pick_file("Select file to copy")
    if source is None:
        _cancelled()
        return
    dest = pick_save_file("Save copy as", initialfile=source.name)
    if dest is None:
        _cancelled()
        return
    copy_file(source, dest)


def _handle_copy_folder() -> None:
    logger.info("Feature: copy folder")
    source = pick_folder("Select folder to copy")
    if source is None:
        _cancelled()
        return
    dest = pick_folder("Select destination parent folder")
    if dest is None:
        _cancelled()
        return
    copy_folder(source, dest / source.name)


def _handle_move_file() -> None:
    logger.info("Feature: move file")
    source = pick_file("Select file to move")
    if source is None:
        _cancelled()
        return
    dest = pick_save_file("Move file to", initialfile=source.name)
    if dest is None:
        _cancelled()
        return
    move_file(source, dest)


def _handle_move_folder() -> None:
    logger.info("Feature: move folder")
    source = pick_folder("Select folder to move")
    if source is None:
        _cancelled()
        return
    dest = pick_folder("Select destination parent folder")
    if dest is None:
        _cancelled()
        return
    move_folder(source, dest / source.name)


def _handle_rename_file() -> None:
    logger.info("Feature: rename file")
    path = pick_file("Select file to rename")
    if path is None:
        _cancelled()
        return
    new_name = Prompt.ask(f"[{style('prompt')}]New filename[/]").strip()
    if not new_name:
        warning("Rename cancelled (empty name).", logger=logger)
        return
    logger.info("Rename file '%s' -> '%s'", path, new_name)
    rename_file(path, new_name)


def _handle_rename_folder() -> None:
    logger.info("Feature: rename folder")
    path = pick_folder("Select folder to rename")
    if path is None:
        _cancelled()
        return
    new_name = Prompt.ask(f"[{style('prompt')}]New folder name[/]").strip()
    if not new_name:
        warning("Rename cancelled (empty name).", logger=logger)
        return
    logger.info("Rename folder '%s' -> '%s'", path, new_name)
    rename_folder(path, new_name)


def _handle_delete() -> None:
    logger.info("Feature: delete to recycle bin")
    kind = Prompt.ask(
        f"[{style('accent')}]Delete[/] [bold]1[/bold] file / [bold]2[/bold] folder",
        choices=["1", "2"],
        show_choices=False,
    )
    if kind == "1":
        path = pick_file("Select file to delete")
    else:
        path = pick_folder("Select folder to delete")
    if path is None:
        _cancelled()
        return
    if not _prompt_yes_no(f"Send [bold]{path.name}[/bold] to the recycle bin?", default=False):
        warning("Delete cancelled.", logger=logger)
        return
    delete_to_recycle_bin(path)


def _handle_sort_by_extension() -> None:
    logger.info("Feature: sort by extension")
    folder = pick_folder("Select folder to sort by extension")
    if folder is None:
        _cancelled()
        return
    sort_by_extension(folder)


def _handle_flatten() -> None:
    logger.info("Feature: flatten folder")
    folder = pick_folder("Select folder to flatten")
    if folder is None:
        _cancelled()
        return
    flatten_folder(folder)


def _handle_unflatten() -> None:
    logger.info("Feature: unflatten folder")
    folder = pick_folder("Select flattened folder")
    if folder is None:
        _cancelled()
        return
    if _prompt_yes_no("Choose a custom output location?", default=False):
        output = pick_folder("Select output root folder")
        if output is None:
            _cancelled()
            return
        unflatten_folder(folder, output)
    else:
        unflatten_folder(folder)


def _handle_compare_folders() -> None:
    logger.info("Feature: compare folders")
    folder_a = pick_folder("Select first folder")
    if folder_a is None:
        _cancelled()
        return
    folder_b = pick_folder("Select second folder")
    if folder_b is None:
        _cancelled()
        return
    recursive = _prompt_yes_no("Include subfolders?", default=True)
    try:
        match, only_a, only_b = compare_folder_filenames_report(
            folder_a, folder_b, recursive=recursive
        )
    except (NotADirectoryError, OSError) as exc:
        error(str(exc), logger=logger)
        return

    if match:
        success("Folders match (same relative file paths).", logger=logger)
        return

    warning("Folders differ.", logger=logger)
    if only_a:
        console.print(
            f"\n[bold]Only in[/bold] [{style('accent')}]{folder_a.name}[/] ({len(only_a)}):"
        )
        for path in sorted(only_a):
            console.print(f"  [{style('bullet')}]•[/] {path}")
            logger.debug("Only in A: %s", path)
    if only_b:
        console.print(
            f"\n[bold]Only in[/bold] [{style('accent')}]{folder_b.name}[/] ({len(only_b)}):"
        )
        for path in sorted(only_b):
            console.print(f"  [{style('bullet')}]•[/] {path}")
            logger.debug("Only in B: %s", path)
    console.print()


def _dispatch(choice: str) -> bool:
    """Run the selected feature. Return False to exit the dashboard."""
    logger.info("Menu choice: %s", choice)
    match choice:
        case "q" | "Q":
            return False
        case "1":
            _handle_copy_file()
        case "2":
            _handle_copy_folder()
        case "3":
            _handle_move_file()
        case "4":
            _handle_move_folder()
        case "5":
            _handle_rename_file()
        case "6":
            _handle_rename_folder()
        case "7":
            _handle_delete()
        case "8":
            _handle_sort_by_extension()
        case "9":
            _handle_flatten()
        case "10":
            _handle_unflatten()
        case "11":
            _handle_compare_folders()
        case _:
            valid = ", ".join(key for key, _ in MENU_ITEMS)
            error(f"Invalid choice '{choice}'. Pick one of: {valid}, or Q to quit.", logger=logger)
    return True


def main() -> None:
    log_path = setup()
    if log_path:
        info(f"Logging to {log_path}", logger=logger)
    info("Opening dashboard… press Q anytime to quit.\n", logger=logger)

    while True:
        _print_dashboard()
        choice = Prompt.ask(f"[{style('prompt')}]Your choice[/]").strip()
        console.print()
        if not _dispatch(choice):
            success("Goodbye!", logger=logger)
            logger.info("Session ended")
            break
        console.print()


if __name__ == "__main__":
    main()
