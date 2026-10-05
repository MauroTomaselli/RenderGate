"""RenderGate File Handler.
Handles reading and writing of .RGE preset text files.
Ensures files are UTF-8 encoded, well-formatted, and human-readable with
reference fields, descriptions, and metadata.
"""

import json
import os
from typing import Dict, Any, Tuple


RGE_EXTENSION = ".RGE"


def save_rge_file(file_path: str, data: Dict[str, Any]) -> Tuple[bool, str]:
    """Saves serialized render preset data to a .RGE text file."""
    if not file_path.upper().endswith(RGE_EXTENSION):
        file_path += RGE_EXTENSION

    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, file_path
    except Exception as e:
        return False, f"Failed to write file '{file_path}': {str(e)}"


def load_rge_file(file_path: str) -> Tuple[bool, Any, str]:
    """Loads a .RGE text file and validates its RenderGate structure.

    Returns:
        (success, parsed_data_or_none, error_message_or_filepath)
    """
    if not os.path.isfile(file_path):
        return False, None, f"File not found: '{file_path}'"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return False, None, "Invalid file format: root object must be a dictionary."

        # Verify that it's a RenderGate file or compatible preset
        if "_rendergate_meta" not in data and "categories" not in data:
            return False, None, "File is not a valid RenderGate (.RGE) preset format."

        return True, data, file_path
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON syntax in '{file_path}': {str(e)}"
    except Exception as e:
        return False, None, f"Error reading '{file_path}': {str(e)}"
