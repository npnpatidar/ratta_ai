"""Export pipeline JSON to Anki TSV + media folder.

Each question becomes one Basic-style note:

    Front: question number + question HTML + options (a)-(d)
    Back:  correct answer letter + full correct option + explanation

HTML for question/options/explanation is produced by
``backend_convert_json_elements_to_html`` (tables, MathML, sub/sup and
inline formatting survive; Anki renders them as-is).

Images are extracted to ``<base>_media/`` (content-hash filenames, so
duplicates are stored once) and ``<img src>`` is rewritten to the bare
filename Anki expects in ``collection.media``.

Usage:
    python main.py json2anki <input_folder> <output_folder>

Import: Anki -> File -> Import -> select ``<name>.txt``
("Text separated by tabs"), map columns to Front/Back, and copy the
``<name>_media`` files into ``collection.media`` (Tools ->
Check Media shows the folder).
"""

import base64
import copy
import hashlib
import json
import os
import re

from bs4 import BeautifulSoup

from src.pipeline_docx import backend_convert_json_elements_to_html

DATA_URI_RE = re.compile(r"data:(image/[\w+.\-]+);base64,(.+)", re.DOTALL)

MIME_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}

OPTION_ORDER = ("a", "b", "c", "d")


def _sanitize_field(text):
    """Strip raw tabs/newlines (they would break TSV rows); <br/> stays."""
    return text.replace("\t", " ").replace("\r", "").replace("\n", " ").strip()


def _save_media_bytes(raw, ext, media_dir, cache):
    key = (hashlib.sha1(raw).hexdigest()[:12], ext)
    if key not in cache:
        filename = f"anki_{key[0]}{ext}"
        with open(os.path.join(media_dir, filename), "wb") as f:
            f.write(raw)
        cache[key] = filename
    return cache[key]


def _save_media_src(src, media_dir, cache):
    """Resolve an <img> src (data-URI or file path) into a media filename."""
    m = DATA_URI_RE.match(src.strip())
    if m:
        mime, b64 = m.group(1).lower(), m.group(2)
        ext = MIME_EXT.get(mime, ".png")
        return _save_media_bytes(base64.b64decode(b64), ext, media_dir, cache)
    with open(src, "rb") as f:
        raw = f.read()
    ext = os.path.splitext(src)[1].lower() or ".png"
    return _save_media_bytes(raw, ext, media_dir, cache)


def _rewrite_html_images(html, media_dir, cache):
    """Rewrite every <img src> in an HTML fragment to a media filename."""
    soup = BeautifulSoup(html, "html.parser")
    changed = False
    for tag in soup.find_all("img"):
        src = tag.get("src")
        if not src or not os.path.basename(src).startswith("anki_"):
            if src:
                tag["src"] = _save_media_src(src, media_dir, cache)
                changed = True
    return str(soup) if changed else html


def _rewrite_table_cell(cell, media_dir, cache):
    if isinstance(cell, list):  # nested table
        return [_rewrite_table_cell(c, media_dir, cache) for c in cell]
    if isinstance(cell, dict) and "type" in cell:  # element dict
        return _rewrite_element(cell, media_dir, cache)
    if isinstance(cell, str) and "<img" in cell:
        return _rewrite_html_images(cell, media_dir, cache)
    return cell


def _rewrite_element(element, media_dir, cache):
    el = copy.deepcopy(element)
    if el.get("type") == "image":
        el["content"] = _rewrite_html_images(el["content"], media_dir, cache)
    elif el.get("type") == "table":
        el["content"] = [
            [_rewrite_table_cell(c, media_dir, cache) for c in row]
            for row in el["content"]
        ]
    return el


def question_to_note(question, media_dir, cache):
    """Convert one question dict to a sanitized (front, back) HTML pair."""
    q_elements = [
        _rewrite_element(e, media_dir, cache) for e in question["question_elements"]
    ]
    o_elements = {
        k: [_rewrite_element(e, media_dir, cache) for e in v]
        for k, v in question["options_elements"].items()
    }
    e_elements = [
        _rewrite_element(e, media_dir, cache) for e in question["explanation_elements"]
    ]

    front = _sanitize_field(question.get("question_num", "")) + " "
    front += backend_convert_json_elements_to_html(q_elements)
    for key in OPTION_ORDER:
        if key in o_elements:
            front += (
                "<p>("
                + key
                + ") "
                + backend_convert_json_elements_to_html(o_elements[key])
                + "</p>"
            )

    answer = (question.get("answer") or "?").strip()
    back = f"<p><strong>Answer: ({answer})</strong>"
    if answer in o_elements:
        back += " " + backend_convert_json_elements_to_html(o_elements[answer])
    back += "</p><p>Exp: " + backend_convert_json_elements_to_html(e_elements) + "</p>"

    return _sanitize_field(front), _sanitize_field(back)


MODEL_ID = 1607392319
DECK_ID = 2059400110

MODEL_CSS = (
    ".card { font-family: arial; font-size: 20px; text-align: left; "
    "color: black; background-color: white; }\n"
    "table { border-collapse: collapse; margin: 8px 0; }\n"
    "td, th { border: 1px solid #888; padding: 4px 8px; }\n"
    "img { max-width: 100%; }\n"
)


def build_model():
    import genanki

    return genanki.Model(
        MODEL_ID,
        "Ratta QA",
        fields=[{"name": "Front"}, {"name": "Back"}],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
            }
        ],
        css=MODEL_CSS,
    )


def build_apkg(txt_path, media_dir, apkg_path, deck_name="Ratta"):
    """Bundle a TSV deck + media folder into a directly importable .apkg."""
    import genanki

    model = build_model()
    deck = genanki.Deck(DECK_ID, deck_name)
    media_files = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            front, back = line.split("\t")
            deck.add_note(
                genanki.Note(
                    model=model,
                    fields=[front, back],
                    guid=genanki.guid_for(front, back),
                )
            )
    if os.path.isdir(media_dir):
        media_files = sorted(os.path.join(media_dir, p) for p in os.listdir(media_dir))
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(apkg_path)
    print(
        f"Anki package written: {len(deck.notes)} notes, "
        f"{len(media_files)} media files -> {apkg_path}"
    )
    return 0


def convert_json_to_apkg(input_file_path, output_file_path):
    """Convert a pipeline .json file directly to an importable ``.apkg``."""
    if not input_file_path.endswith(".json"):
        raise ValueError(f"expected a .json input file, got: {input_file_path}")
    base, _ = os.path.splitext(output_file_path)
    txt_path = base + ".txt"
    media_dir = base + "_media"
    apkg_path = base + ".apkg"
    convert_json_to_anki(input_file_path, output_file_path)
    deck_name = os.path.splitext(os.path.basename(input_file_path))[0]
    return build_apkg(txt_path, media_dir, apkg_path, deck_name)


def convert_json_to_anki(input_file_path, output_file_path):
    """Convert a pipeline .json file to ``<base>.txt`` + ``<base>_media/``."""
    if not input_file_path.endswith(".json"):
        raise ValueError(f"expected a .json input file, got: {input_file_path}")
    base, _ = os.path.splitext(output_file_path)
    txt_path = base + ".txt"
    media_dir = base + "_media"
    os.makedirs(media_dir, exist_ok=True)

    with open(input_file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    cache = {}
    lines = []
    for question in questions:
        front, back = question_to_note(question, media_dir, cache)
        lines.append(f"{front}\t{back}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"Anki deck written: {len(lines)} notes -> {txt_path} "
        f"({len(cache)} media files in {media_dir})"
    )
    return 0
