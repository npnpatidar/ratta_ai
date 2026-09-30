"""Shared helpers for the DOCX <-> JSON pipeline."""

import os


def writeLog(message):
    """Append a single log line (UTF-8, no leading blank line)."""
    with open("process.log", "a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def process_folder_for_given_function(
    input_folder, output_folder, process_function, file_or_folder="files"
):
    """Recursively apply process_function, preserving folder structure.

    Raises:
        FileNotFoundError: if input_folder does not exist.
        NotADirectoryError: if input_folder is not a directory.
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"input folder not found: {input_folder}")
    if not os.path.isdir(input_folder):
        raise NotADirectoryError(f"input path is not a directory: {input_folder}")
    total = 0
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, _directories, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)
        print(process_function.__name__.__str__() + "           " + root)
        if file_or_folder == "files":
            for filename in files:
                input_file_path = os.path.join(root, filename)
                output_file_path = os.path.join(output_subfolder, filename)
                total += process_function(input_file_path, output_file_path)
                print(process_function.__name__.__str__() + "           " + filename)
        else:
            total += process_function(root, output_subfolder)
    return total
