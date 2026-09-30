"""Backward-compat shim. Legacy TXT pipeline lives in src.pipeline_txt; shared in src.common.

Canonical pipeline for new work: src.pipeline_docx.
"""
from src.pipeline_txt import *  # noqa
from src.common import (  # noqa
    append_to_json_file,
    backend_create_folders_and_files,
    backend_folder_to_json,
    combine_json_files,
    create_folder_structure_from_yaml,
    get_max_column_width,
    process_folder_for_given_function,
    save_folder_structure_into_yaml,
    set_cell_border,
    set_column_widths,
    set_font,
    update_file_names_in_a_folder,
    write_json,
    write_yaml,
    writeLog,
    setup_logger,
)
