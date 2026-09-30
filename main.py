"""Batch convert a whole folder recursively: docx -> json or json -> docx.

Usage:
    python main.py docx2json <input_folder> <output_folder>
    python main.py json2docx <input_folder> <output_folder>
    python main.py json2anki <input_folder> <output_folder>
    python main.py json2apkg <input_folder> <output_folder>

Only matching files are converted (.docx / .json); others are skipped.
One bad file does not stop the run — failures are reported at the end.
json2anki writes <name>.txt + <name>_media/ per input file.
"""

import sys
import traceback

from src.common import process_folder_for_given_function, writeLog
from src.export_anki import convert_json_to_anki, convert_json_to_apkg
from src.pipeline_docx import convert_docx_to_json, convert_json_to_docx

MODES = {
    "docx2json": ((".docx",), convert_docx_to_json),
    "json2docx": ((".json",), convert_json_to_docx),
    "json2anki": ((".json",), convert_json_to_anki),
    "json2apkg": ((".json",), convert_json_to_apkg),
}


def _filtered(exts, fn):
    def run(input_file, output_file):
        if not input_file.lower().endswith(exts):
            print(f"skip (not {exts}): {input_file}")
            return 0
        try:
            fn(input_file, output_file)
            return 1
        except Exception as e:  # keep going; report at the end
            msg = f"FAILED {input_file}: {e}"
            print(msg)
            writeLog(msg)
            writeLog(traceback.format_exc())
            run.failures.append(input_file)
            return 0

    run.__name__ = fn.__name__
    run.failures = []
    return run


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3 or argv[0] not in MODES:
        print(__doc__)
        return 1
    exts, fn = MODES[argv[0]]
    runner = _filtered(exts, fn)
    try:
        total = process_folder_for_given_function(argv[1], argv[2], runner, "files")
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"error: {e}")
        return 1
    print(f"Done: {total} files converted ({argv[0]})")
    if runner.failures:
        print(f"Failures ({len(runner.failures)}):")
        for f in runner.failures:
            print(f"  {f}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
