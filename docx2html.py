"""Backward-compat shim. Canonical: src.pipeline_docx."""
from src.pipeline_docx import *  # noqa
from src.common import (  # noqa - helpers previously reached via ratta_functions
    append_to_json_file, process_folder_for_given_function, writeLog,
    write_json, write_yaml,
)
