"""Battle test: json -> docx -> json round trip over many variations.

Covers: plain text, Hindi/unicode, tables (in question/option/
explanation), images (data-URI + file path), MathML equations,
chemistry sub/sup markup, inline formatting tags, special chars
(&, <, >), multiline text. Also asserts double round-trip idempotency.

Needs: python-docx, pypandoc (+ pandoc binary), beautifulsoup4.
Run: pytest tests/test_roundtrip.py
"""

import base64
import json
import re

import pytest

from src.pipeline_docx import convert_docx_to_json, convert_json_to_docx

# 1x1 red PNG (no PIL needed to build fixtures)
RED_PX_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
    "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

MATHML = (
    '<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML">'
    "<mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>2</mn>"
    "<mi>x</mi><mo>+</mo><mn>1</mn><mo>=</mo><mn>0</mn></mrow></math>"
)


def T(c):
    return {"type": "text", "content": c}


def I(c):
    return {"type": "image", "content": c}


def Tb(rows):
    return {"type": "table", "content": rows}


def build_questions(img_path):
    data_uri = "data:image/png;base64," + RED_PX_B64
    return [
        {
            "question_num": "1.)",
            "question_elements": [T("What is the capital of France?")],
            "options_elements": {
                "a": [T("London")],
                "b": [T("Paris")],
                "c": [T("Berlin")],
                "d": [T("Rome")],
            },
            "answer": "b",
            "explanation_elements": [T("Paris is the capital of France.")],
        },
        {
            "question_num": "2.)",
            "question_elements": [
                T("अकबर ने राणा प्रताप को समझाने के लिए प्रथम दूत के रूप में किसे भेजा?")
            ],
            "options_elements": {
                "a": [T("टोडरमल")],
                "b": [T("जलाल खाँ")],
                "c": [T("मानसिंह")],
                "d": [T("भगवानदास")],
            },
            "answer": "b",
            "explanation_elements": [T("जलाल खाँ नवम्बर 1572 में भेजा गया था।")],
        },
        {
            "question_num": "3.)",
            "question_elements": [
                T("Match the following:"),
                Tb([["A", "B"], ["1. जलाल खाँ", "नवम्बर 1572"]]),
            ],
            "options_elements": {
                "a": [T("1-A")],
                "b": [T("1-B")],
                "c": [T("Both")],
                "d": [T("None")],
            },
            "answer": "a",
            "explanation_elements": [T("See table above.")],
        },
        {
            "question_num": "4.)",
            "question_elements": [
                T("Identify the shape:"),
                I('<br/><img src="' + data_uri + '" />'),
            ],
            "options_elements": {
                "a": [T("Circle")],
                "b": [T("Square")],
                "c": [T("Triangle")],
                "d": [T("Star")],
            },
            "answer": "b",
            "explanation_elements": [T("Red square.")],
        },
        {
            "question_num": "5.)",
            "question_elements": [
                T("What colour is the pixel?"),
                I('<br/><img src="' + str(img_path) + '" />'),
            ],
            "options_elements": {
                "a": [T("Red")],
                "b": [T("Blue")],
                "c": [T("Green")],
                "d": [T("Yellow")],
            },
            "answer": "a",
            "explanation_elements": [
                T("Explanation table:"),
                Tb([["Col1", "Col2"], ["v1", "v2"]]),
                I('<br/><img src="' + str(img_path) + '" />'),
            ],
        },
        {
            "question_num": "6.)",
            "question_elements": [T("Solve: " + MATHML + " What is x?")],
            "options_elements": {
                "a": [T("x = 1")],
                "b": [T("x = -1")],
                "c": [T("x = 0")],
                "d": [T("x = 2")],
            },
            "answer": "b",
            "explanation_elements": [T("Perfect square: (x+1)^2 = 0.")],
        },
        {
            "question_num": "7.)",
            "question_elements": [
                T("Balance: H<sub>2</sub> + O<sub>2</sub> → H<sub>2</sub>O?")
            ],
            "options_elements": {
                "a": [T("1")],
                "b": [T("2")],
                "c": [T("3")],
                "d": [T("4")],
            },
            "answer": "b",
            "explanation_elements": [
                T(
                    "2H<sub>2</sub> + O<sub>2</sub> → 2H<sub>2</sub>O at 10<sup>-3</sup> M."
                )
            ],
        },
        {
            "question_num": "8.)",
            "question_elements": [T("Which table is correct?")],
            "options_elements": {
                "a": [Tb([["X", "Y"], ["1", "2"]])],
                "b": [T("No table")],
                "c": [T("Both")],
                "d": [T("None")],
            },
            "answer": "a",
            "explanation_elements": [T("Option (a) has the table.")],
        },
        {
            "question_num": "9.)",
            "question_elements": [
                T("If A & B are true and C < D > E, which holds?\nSecond line.")
            ],
            "options_elements": {
                "a": [T("A & B")],
                "b": [T("C < D")],
                "c": [T("E > F")],
                "d": [T("100% sure")],
            },
            "answer": "a",
            "explanation_elements": [T("A & B holds.\nMultiline with 5 < 6.")],
        },
        {
            "question_num": "10.)",
            "question_elements": [
                T("Which word is <strong>important</strong> and <em>emphasized</em>?")
            ],
            "options_elements": {
                "a": [T("<u>underlined</u> option")],
                "b": [T("plain")],
                "c": [T("<del>deleted</del>")],
                "d": [T("<mark>marked</mark>")],
            },
            "answer": "a",
            "explanation_elements": [T("Formatting <strong>preserved</strong>?")],
        },
    ]


def norm_text(s):
    # Pandoc wraps MathML in <semantics> + tex annotation: semantically equal.
    s = re.sub(r"<annotation.*?</annotation>", "", s, flags=re.DOTALL)
    s = re.sub(r"</?semantics>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def flat(section):
    if isinstance(section, list):
        return section
    return [e for v in section.values() for e in v]


def assert_same_questions(orig, back):
    assert len(orig) == len(back)
    for o, b in zip(orig, back):
        assert o["question_num"] == b["question_num"]
        assert o["answer"] == b["answer"]
        for sec in ("question_elements", "options_elements", "explanation_elements"):
            oe, be = flat(o[sec]), flat(b[sec])
            assert len(oe) == len(be), (o["question_num"], sec, oe, be)
            for a, c in zip(oe, be):
                assert a["type"] == c["type"], (o["question_num"], sec)
                if a["type"] == "text":
                    assert norm_text(a["content"]) == norm_text(c["content"]), (
                        o["question_num"],
                        sec,
                        a["content"][:120],
                        c["content"][:120],
                    )
                elif a["type"] == "table":
                    assert a["content"] == c["content"], (o["question_num"], sec)
                # images: bytes get re-encoded by pandoc; presence is asserted


def test_roundtrip(tmp_path):
    img = tmp_path / "px.png"
    img.write_bytes(base64.b64decode(RED_PX_B64))
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps(build_questions(img), ensure_ascii=False), encoding="utf-8"
    )
    docx = tmp_path / "mid.docx"
    back_p = tmp_path / "back.json"
    assert convert_json_to_docx(str(src), str(docx)) == 0
    assert convert_docx_to_json(str(docx), str(back_p)) == 0
    back = json.loads(back_p.read_text(encoding="utf-8"))
    orig = json.loads(src.read_text(encoding="utf-8"))
    assert_same_questions(orig, back)


def test_double_roundtrip_idempotent(tmp_path):
    img = tmp_path / "px.png"
    img.write_bytes(base64.b64decode(RED_PX_B64))
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps(build_questions(img), ensure_ascii=False), encoding="utf-8"
    )
    d1, j1 = tmp_path / "m1.docx", tmp_path / "b1.json"
    d2, j2 = tmp_path / "m2.docx", tmp_path / "b2.json"
    convert_json_to_docx(str(src), str(d1))
    convert_docx_to_json(str(d1), str(j1))
    convert_json_to_docx(str(j1), str(d2))
    convert_docx_to_json(str(d2), str(j2))
    assert json.loads(j1.read_text(encoding="utf-8")) == json.loads(
        j2.read_text(encoding="utf-8")
    )


def test_malformed_docx_raises(tmp_path):
    from docx import Document

    bad = tmp_path / "bad.docx"
    doc = Document()
    doc.add_paragraph("This document has no numbered questions at all.")
    doc.save(str(bad))
    out = tmp_path / "o.json"
    with pytest.raises(ValueError):
        convert_docx_to_json(str(bad), str(out))
