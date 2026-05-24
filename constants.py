# Feature constants loaded from config.json (single source of truth).
from app_io import get_config, setup

setup()

_features = get_config()["features"]

FLATTEN_SEPARATOR: str = _features["flatten_separator"]
FLATTEN_OUTPUT_SUFFIX: str = _features["flatten_output_suffix"]
DELETE_FALLBACK_FOLDER: str = _features["delete_fallback_folder"]
NO_EXTENSION_FOLDER: str = _features["no_extension_folder"]
