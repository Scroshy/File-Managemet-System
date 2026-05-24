"""Shared configuration, logging, and Rich console output for the app."""

import json
import logging
from datetime import datetime
from pathlib import Path

from rich.console import Console

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ROOT_DIR / "config.json"

_config: dict | None = None
_console: Console | None = None
_setup_done = False


def root_logger_name() -> str:
    return get_config()["logging"]["root_logger_name"]


def load_config() -> dict:
    """Load application settings from config.json."""
    global _config
    if _config is not None:
        return _config
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        _config = json.load(fh)
    return _config


def get_config() -> dict:
    if _config is None:
        return load_config()
    return _config


def style(key: str) -> str:
    """Return a Rich style string from config."""
    return get_config()["rich"]["styles"][key]


def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console()
    return _console


def setup() -> Path | None:
    """
    Initialize logging (file) and Rich console from config.json.

    Returns the log file path when logging is enabled, else None.
    """
    global _setup_done
    if _setup_done:
        return _log_file_path()

    config = load_config()
    get_console()

    log_path: Path | None = None
    if config["logging"]["enabled"]:
        log_cfg = config["logging"]
        logs_dir = ROOT_DIR / log_cfg["logs_directory"]
        logs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = log_cfg["log_filename"].format(timestamp=timestamp)
        log_path = logs_dir / filename

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                log_cfg["file_format"],
                datefmt=log_cfg["date_format"],
            )
        )

        root = logging.getLogger(root_logger_name())
        root.setLevel(getattr(logging, log_cfg["level"].upper(), logging.DEBUG))
        root.handlers.clear()
        root.addHandler(file_handler)
        root.propagate = False

        root.info("Session started")
        root.info("Config loaded from %s", CONFIG_PATH)
        root.debug("Log file: %s", log_path)

    _setup_done = True
    return log_path


def _log_file_path() -> Path | None:
    config = get_config()
    if not config["logging"]["enabled"]:
        return None
    logs_dir = ROOT_DIR / config["logging"]["logs_directory"]
    if not logs_dir.exists():
        return None
    files = sorted(logs_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the app root logger."""
    setup()
    root = root_logger_name()
    if name.startswith(f"{root}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{root}.{name}")


def _emit(level: int, message: str, style_key: str, logger: logging.Logger) -> None:
    logger.log(level, message)
    if not get_config()["rich"]["enabled"]:
        print(message)
        return
    get_console().print(message, style=style(style_key))


def info(message: str, *, logger: logging.Logger | None = None) -> None:
    _emit(logging.INFO, message, "info", logger or get_logger("app"))


def success(message: str, *, logger: logging.Logger | None = None) -> None:
    _emit(logging.INFO, message, "success", logger or get_logger("app"))


def warning(message: str, *, logger: logging.Logger | None = None) -> None:
    _emit(logging.WARNING, message, "warning", logger or get_logger("app"))


def error(message: str, *, logger: logging.Logger | None = None) -> None:
    _emit(logging.ERROR, message, "error", logger or get_logger("app"))


def debug(message: str, *, logger: logging.Logger | None = None) -> None:
    _emit(logging.DEBUG, message, "debug", logger or get_logger("app"))
