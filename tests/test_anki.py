"""Tests for src.export_anki (JSON -> Anki TSV + media)."""

import base64
import json
import os

import pytest

from src.export_anki import (
    build_apkg,
    convert_json_to_anki,
    convert_json_to_apkg,
    question_to_note,
)

RED_PX_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
    "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

MATHML = (
    '<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML">'
    "<mrow><msup><mi>x</mi><mn>2</mn></msup><mo>=</mo><mn>1</mn></mrow></math>"
)


def T(c):
    return {"type": "text", "content": c}


def build_question(img_src):
    return {
        "question_num": "1.)",
        "question_elements": [
            T("Solve: " + MATHML),
            {"type": "image", "content": '<br/><img src="' + img_src + '" />'},
            {"type": "table", "content": [["A", "B"], ["1", "2"]]},
        ],
        "options_elements": {
            "a": [T("x = 1")],
            "b": [T("x = -1")],
            "c": [T("H<sub>2</sub>O")],
            "d": [T("plain")],
        },
        "answer": "b",
        "explanation_elements": [T("Because (x+1)(x-1) = 0.")],
    }


def test_data_uri_image_extracted_to_media(tmp_path):
    q = build_question("data:image/png;base64," + RED_PX_B64)
    front, back = question_to_note(q, str(tmp_path), {})
    media = list(tmp_path.iterdir())
    assert len(media) == 1 and media[0].suffix == ".png"
    assert media[0].read_bytes() == base64.b64decode(RED_PX_B64)
    assert f'src="{media[0].name}"' in front
    assert "data:" not in front


def test_file_path_image_copied_to_media(tmp_path):
    img = tmp_path / "src.png"
    img.write_bytes(base64.b64decode(RED_PX_B64))
    media = tmp_path / "media"
    media.mkdir()
    q = build_question(str(img))
    front, _ = question_to_note(q, str(media), {})
    files = list(media.iterdir())
    assert len(files) == 1 and files[0].read_bytes() == img.read_bytes()
    assert f'src="{files[0].name}"' in front


def test_duplicate_images_deduplicated(tmp_path):
    src = "data:image/png;base64," + RED_PX_B64
    q = build_question(src)
    q["explanation_elements"].append(
        {"type": "image", "content": '<br/><img src="' + src + '" />'}
    )
    front, back = question_to_note(q, str(tmp_path), {})
    assert len(list(tmp_path.iterdir())) == 1


def test_front_has_options_back_has_answer(tmp_path):
    front, back = question_to_note(
        build_question("data:image/png;base64," + RED_PX_B64), str(tmp_path), {}
    )
    for key in ("(a)", "(b)", "(c)", "(d)"):
        assert key in front
    assert MATHML in front
    assert "<table" in front
    assert "H<sub>2</sub>O" in front
    assert "Answer: (b)" in back
    assert "x = -1" in back  # full correct option text resolved
    assert "Exp:" in back


def test_tsv_rows_are_clean_two_column(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps([build_question("data:image/png;base64," + RED_PX_B64)]),
        encoding="utf-8",
    )
    assert convert_json_to_anki(str(src), str(tmp_path / "in.json")) == 0
    txt = tmp_path / "in.txt"
    rows = txt.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    cols = rows[0].split("\t")
    assert len(cols) == 2
    assert all("\t" not in c and "\n" not in c and "\r" not in c for c in cols)
    assert (tmp_path / "in_media").is_dir()


def test_rejects_non_json(tmp_path):
    bad = tmp_path / "in.txt"
    bad.write_text("hi", encoding="utf-8")
    with pytest.raises(ValueError):
        convert_json_to_anki(str(bad), str(tmp_path / "o.txt"))
    with pytest.raises(ValueError):
        convert_json_to_apkg(str(bad), str(tmp_path / "o.txt"))


def test_missing_answer_does_not_crash(tmp_path):
    q = build_question("data:image/png;base64," + RED_PX_B64)
    q["answer"] = ""
    front, back = question_to_note(q, str(tmp_path), {})
    assert "Answer: (?)" in back


def test_cli_json2anki(tmp_path):
    from main import main

    src = tmp_path / "in"
    src.mkdir()
    (src / "q.json").write_text(
        json.dumps([build_question("data:image/png;base64," + RED_PX_B64)]),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    assert main(["json2anki", str(src), str(out)]) == 0
    assert (out / "q.txt").exists()
    assert (out / "q_media").is_dir()
    assert len(os.listdir(out / "q_media")) == 1


def _apkg_notes(apkg_path):
    import sqlite3
    import zipfile

    with zipfile.ZipFile(apkg_path) as z:
        names = z.namelist()
        assert "collection.anki2" in names
        z.extract("collection.anki2", path=str(apkg_path.parent))
    db = apkg_path.parent / "collection.anki2"
    try:
        con = sqlite3.connect(str(db))
        try:
            return con.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        finally:
            con.close()
    finally:
        db.unlink()


def test_build_apkg_valid_package(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps(
            [
                build_question("data:image/png;base64," + RED_PX_B64),
                build_question("data:image/png;base64," + RED_PX_B64),
            ]
        ),
        encoding="utf-8",
    )
    assert convert_json_to_apkg(str(src), str(tmp_path / "in.json")) == 0
    apkg = tmp_path / "in.apkg"
    assert apkg.exists() and apkg.stat().st_size > 0
    assert _apkg_notes(apkg) == 2
    import zipfile

    with zipfile.ZipFile(apkg) as z:
        # 'media' is genanki's filename manifest; the rest are media blobs.
        media_files = [
            n for n in z.namelist() if n not in ("collection.anki2", "media")
        ]
    assert len(media_files) == 1  # duplicate image stored once


def test_cli_json2apkg(tmp_path):
    from main import main

    src = tmp_path / "in"
    src.mkdir()
    (src / "q.json").write_text(
        json.dumps([build_question("data:image/png;base64," + RED_PX_B64)]),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    assert main(["json2apkg", str(src), str(out)]) == 0
    apkg = out / "q.apkg"
    assert apkg.exists()
    assert _apkg_notes(apkg) == 1
