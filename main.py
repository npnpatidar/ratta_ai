"""CLI entry. Canonical logic lives in src/."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.common import setup_logger
from src.pipeline_docx import get_initial_idea_of_files_from_a_folder_recursively

DEFAULT_INPUT = "/home/naresh/Work/Working/input"
DEFAULT_OUTPUT = "/home/naresh/Work/Working/output"


def main(input_folder=DEFAULT_INPUT, output_folder=DEFAULT_OUTPUT):
    setup_logger("process.log")
    get_initial_idea_of_files_from_a_folder_recursively(input_folder)
    get_initial_idea_of_files_from_a_folder_recursively(output_folder)


if __name__ == "__main__":
    in_folder = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    out_folder = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT
    main(in_folder, out_folder)
