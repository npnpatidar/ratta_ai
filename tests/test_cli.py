"""CLI + hardening tests for main.py / src.common.

Covers the audit gaps: exit codes, missing input dir, non-.json input
rejected loudly, skipped extensions, and special-char answers surviving
a json -> docx -> json round trip.
"""

import json

import pytest

from main import _filtered, main
from src.common import process_folder_for_given_function
from src.pipeline_docx import convert_docx_to_json, convert_json_to_docx


def test_cli_usage_error_no_args():
    assert main([]) == 1


def test_cli_usage_error_bad_mode(tmp_path):
    assert main(["nope", str(tmp_path), str(tmp_path)]) == 1


def test_cli_missing_input_dir(tmp_path):
    missing = tmp_path / "does-not-exist"
    out = tmp_path / "out"
    assert main(["docx2json", str(missing), str(out)]) == 1


def test_process_folder_rejects_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_folder_for_given_function(
            str(tmp_path / "missing"), str(tmp_path / "o"), lambda a, b: 0
        )


def test_process_folder_rejects_file_as_input(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        process_folder_for_given_function(str(f), str(tmp_path / "o"), lambda a, b: 0)


def test_convert_json_to_docx_rejects_non_json(tmp_path):
    bad = tmp_path / "in.txt"
    bad.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        convert_json_to_docx(str(bad), str(tmp_path / "o.docx"))


def test_filtered_skips_wrong_extension():
    calls = []

    def fn(a, b):
        calls.append((a, b))
        return 1

    runner = _filtered((".json",), fn)
    assert runner("/x/notes.txt", "/y/notes.txt") == 0
    assert calls == []
    assert runner.failures == []


def test_filtered_collects_failures_instead_of_raising(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def boom(a, b):
        raise RuntimeError("kablam")

    runner = _filtered((".json",), boom)
    assert runner("a.json", "b.json") == 0
    assert runner.failures == ["a.json"]
    assert "kablam" in (tmp_path / "process.log").read_text(encoding="utf-8")


def test_special_char_answer_roundtrip(tmp_path):
    q = {
        "question_num": "1.)",
        "question_elements": [
            {"type": "text", "content": "If A & B and C < D > E, pick %100?"}
        ],
        "options_elements": {
            "a": [{"type": "text", "content": "A & B"}],
            "b": [{"type": "text", "content": "C < D"}],
            "c": [{"type": "text", "content": "E > F"}],
            "d": [{"type": "text", "content": "100% <sure> & safe"}],
        },
        "answer": "a & b <c>",
        "explanation_elements": [{"type": "text", "content": "5 < 6 & 7 > 2."}],
    }
    src = tmp_path / "in.json"
    src.write_text(json.dumps([q], ensure_ascii=False), encoding="utf-8")
    docx = tmp_path / "mid.docx"
    back_p = tmp_path / "back.json"
    assert convert_json_to_docx(str(src), str(docx)) == 0
    assert convert_docx_to_json(str(docx), str(back_p)) == 0
    back = json.loads(back_p.read_text(encoding="utf-8"))
    assert back[0]["answer"] == "a & b <c>"


def test_cli_json2docx_failure_exit_code(tmp_path, monkeypatch):
    """A corrupt .json counts as failure (exit 2), not success."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "in"
    src.mkdir()
    (src / "bad.json").write_text("{not valid json", encoding="utf-8")
    out = tmp_path / "out"
    assert main(["json2docx", str(src), str(out)]) == 2
