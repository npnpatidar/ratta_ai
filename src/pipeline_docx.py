"""DOCX <-> JSON question pipeline (canonical).

Only laissez: convert_docx_to_json / convert_json_to_docx + their callees.
"""

import json
import os
import re
import tempfile
import html as _html

import pypandoc
from bs4 import BeautifulSoup
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


_ALLOWED_INLINE_TAGS = (
    r"<math.*?</math>|<br\s*/?>|</?(?:strong|em|u|del|mark|sub|sup)(?:\s[^>]*)?/?>"
)
_ALLOWED_INLINE_RE = re.compile(f"({_ALLOWED_INLINE_TAGS})", flags=re.DOTALL)


def update_font_style_in_docx(input_file_path, output_file_path):

    def set_column_widths_auto(doc):
        for table in doc.tables:
            for column in table.columns:
                for cell in column.cells:
                    tc = cell._tc
                    tcPr = tc.get_or_add_tcPr()
                    tcW = tcPr.get_or_add_tcW()
                    tcW.type = "auto"
                    tcW.w = 0

    def set_cell_border(doc):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    tc = cell._element
                    tcPr = tc.get_or_add_tcPr()
                    tcW = tcPr.get_or_add_tcW()
                    tcW.type = "auto"
                    tcBorders = tcPr.find(qn("w:tcBorders"))
                    if tcBorders is None:
                        tcBorders = OxmlElement("w:tcBorders")
                        tcPr.append(tcBorders)
                    for border in ["top", "left", "bottom", "right"]:
                        tcBorder = OxmlElement(f"w:{border}")
                        tcBorder.set(qn("w:val"), "single")
                        tcBorder.set(qn("w:sz"), "4")
                        tcBorder.set(qn("w:space"), "0")
                        tcBorder.set(qn("w:color"), "000000")
                        tcBorders.append(tcBorder)

    def set_font(paragraph, font_name, font_size):
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            # Ensure the font name is set correctly
            rPr = run._element.get_or_add_rPr()
            rFonts = OxmlElement("w:rFonts")
            rFonts.set(qn("w:ascii"), font_name)
            rFonts.set(qn("w:hAnsi"), font_name)
            rFonts.set(qn("w:eastAsia"), font_name)
            rFonts.set(qn("w:cs"), font_name)
            rPr.append(rFonts)

    # Load the document
    doc = Document(input_file_path)
    font_name = "Sahitya"
    font_size = 12

    # Change the font for all paragraphs in the document
    for paragraph in doc.paragraphs:
        set_font(paragraph, font_name, font_size)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    set_font(paragraph, font_name, font_size)

    # Format all tables in the document

    set_cell_border(doc)
    set_column_widths_auto(doc)
    # set_column_widths_manually(doc)

    # Save the modified document
    doc.save(output_file_path)

    return 0


def backend_clean_html(html):
    def backend_replace_options_in_table(match):
        table_html = match.group(0)
        # More specific replacement within <td> or <th> tags only
        table_html = re.sub(r"\(a\)", "(A)", table_html, flags=re.IGNORECASE)
        table_html = re.sub(r"\(b\)", "(B)", table_html, flags=re.IGNORECASE)
        table_html = re.sub(r"\(c\)", "(C)", table_html, flags=re.IGNORECASE)
        table_html = re.sub(r"\(d\)", "(D)", table_html, flags=re.IGNORECASE)
        return table_html

    # Apply the function to each table in the HTML
    html = re.sub(
        r"(<table.*?>.*?</table>)",
        backend_replace_options_in_table,
        html,
        flags=re.DOTALL,
    )

    html = re.sub(
        r"<((?:strong|sup|sub|mark|em|u|del))><br />\s*\n</\1>",
        "<br />\n",
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"<((?:strong|sup|sub|mark|em|u|del))><br />\s*\n</\1>",
        "<br />\n",
        html,
        flags=re.MULTILINE,
    )

    # Continue with the existing cleanup operations
    html = re.sub(r"^(\d+\.\))", r"</p>\n<p>\1", html, flags=re.MULTILINE)
    html = re.sub(r"^\((a|b|c|d)\)", r"</p>\n<p>(\1)", html, flags=re.MULTILINE)
    html = re.sub(r"^Ans\.", r"</p>\n<p>Ans.", html, flags=re.MULTILINE)
    html = re.sub(r"^Exp:", "</p>\n<p>Exp:", html, flags=re.MULTILINE)

    html = re.sub(r"(?<!</p>)\n(?!<p>)", " ", html)
    html = re.sub(r"</p>\n<p>", "\n", html, flags=re.DOTALL)

    html = re.sub(r"<br />", "\n", html, flags=re.DOTALL)
    html = re.sub(r"<strong>\s*\n\s*</strong>", "", html, flags=re.DOTALL)
    html = re.sub(r"<u>\s*\n\s*</u>", "", html, flags=re.DOTALL)
    html = re.sub(r"<em>\s*\n\s*</em>", "", html, flags=re.DOTALL)
    html = re.sub(r"<del>\s*\n\s*</del>", "", html, flags=re.DOTALL)
    html = re.sub(r"<mark>\s*\n\s*</mark>", "", html, flags=re.DOTALL)
    # Decode HTML entities (&amp; -> &, &lt; -> <, ...) so literal
    # &, <, > in question text survive the round trip. Non-breaking
    # spaces become regular spaces.
    html = _html.unescape(html)
    html = html.replace("\xa0", " ")
    html = re.sub(r"\n<math", " <math", html)
    html = re.sub(r"\n</math>", " </math>\n", html)
    html = re.sub(r"</math><br/>", " </math> ", html)
    html = re.sub(r"<body>.<p>", "<body>\n", html, flags=re.DOTALL)
    # Replace multiple newlines with a single newline
    html = re.sub(r"\n\n+", "\n", html)
    html = re.sub(r"<p>", "", html)
    html = re.sub(r"</p>", "", html)
    html = re.sub(r"</body> </html>", "", html)
    return html


def backend_extract_html_elements(text):

    def parse_content(contents):
        for content in contents:
            if (
                isinstance(content, str)
                or content.name == "math"
                or content.name == "strong"
                or content.name == "em"
                or content.name == "u"
                or content.name == "del"
                or content.name == "mark"
                or content.name == "sub"
                or content.name == "sup"
            ):
                content_str = content if isinstance(content, str) else str(content)
                if elements and elements[-1]["type"] == "text":
                    elements[-1]["content"] += content_str
                else:
                    elements.append({"type": "text", "content": content_str})
            elif content.name == "img":
                elements.append({"type": "image", "content": ("<br/>" + str(content))})
            elif content.name == "table":
                elements.append(
                    {
                        "type": "table",
                        "content": backend_convert_table_to_json(str(content)),
                    }
                )
            else:
                parse_content(content.contents)

    soup = BeautifulSoup(text, "html.parser")
    elements = []

    parse_content(soup.contents)
    # Drop whitespace-only text elements (e.g. stray newlines around
    # images/tables) — they are noise, not content.
    elements = [
        e for e in elements if not (e["type"] == "text" and e["content"].strip() == "")
    ]
    return elements


def _escape_text_preserving_markup(content):
    """Escape HTML special chars, leaving allowed inline tags intact."""
    parts = _ALLOWED_INLINE_RE.split(content)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)  # allowed tag — keep verbatim
        else:
            out.append(_html.escape(part, quote=False))
    return "".join(out)


def backend_convert_json_elements_to_html(elements):
    html_content = ""
    for element in elements:
        if element["type"] == "text":
            formatted_text = _escape_text_preserving_markup(element["content"]).replace(
                "\n", "<br/>"
            )
            html_content += formatted_text

        elif element["type"] == "image":
            # Strip trailing line breaks before an image/table so repeated
            # round trips don't accumulate blank lines (the stored "<br/>"
            # prefix on images already provides the break).
            html_content = re.sub(r"(<br/>|\s)+$", "", html_content)
            html_content += element["content"]
        elif element["type"] == "table":
            html_content = re.sub(r"(<br/>|\s)+$", "", html_content)
            html_content += backend_convert_table_from_json(element["content"])

    # html_content = html_content.replace('<math>', '<math>')
    html_content = html_content.replace("</math><br/>", "</math> ")
    return html_content


def backend_convert_table_from_json(table_json):
    """Converts a JSON representation of a table into HTML format."""
    table_html = '<table border="1">'
    for row in table_json:
        table_html += "<tr>"
        for cell in row:
            table_html += "<td>"
            # Handle each cell using convert_elements_to_html for recursive processing
            if isinstance(cell, list):
                # If the cell is a list, treat it as a nested table
                table_html += backend_convert_table_from_json(cell)
            elif isinstance(cell, dict) and "type" in cell:
                # If the cell is a dictionary with a 'type', treat it as an element
                table_html += backend_convert_json_elements_to_html([cell])
            else:
                # Otherwise, treat it as plain text and replace new lines with <br/>
                table_html += str(cell).replace("\n", "<br/>")
            table_html += "</td>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html


def backend_convert_table_to_json(table_html):
    soup = BeautifulSoup(table_html, "html.parser")
    table = []
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        row_content = []
        for cell in cells:
            cell_html = (
                str(cell)
                .replace("<td>", "")
                .replace("</td>", "")
                .replace("<th>", "")
                .replace("</th>", "")
            )
            row_content.append(cell_html)
        table.append(row_content)
    return table


def convert_docx_to_json(input_file_path, output_file_path):

    def extract_question_data(input_text):
        # Split the text to get the explanation part
        parts = input_text.split("\nExp:")
        explanation = parts[1].strip() if len(parts) > 1 else ""

        # Get the answer part
        parts = parts[0].split("\nAns.")
        answer = parts[1].strip() if len(parts) > 1 else ""

        # Extract options by splitting from the last occurrences of the option labels
        options_text = parts[0]

        # Extract option (d)
        parts = options_text.rsplit("\n(d)", 1)
        option_d = parts[1].strip() if len(parts) > 1 else ""

        # Extract option (c)
        parts = parts[0].rsplit("\n(c)", 1)
        option_c = parts[1].strip() if len(parts) > 1 else ""

        # Extract option (b)
        parts = parts[0].rsplit("\n(b)", 1)
        option_b = parts[1].strip() if len(parts) > 1 else ""

        # Extract option (a) and the question text
        parts = parts[0].rsplit("\n(a)", 1)
        option_a = parts[1].strip() if len(parts) > 1 else ""
        question_text = parts[0].strip()

        # Extract the question number and question
        question_parts = question_text.split(".)", 1)
        question_number = question_parts[0].strip() if len(question_parts) > 1 else ""
        question = question_parts[1].strip() if len(question_parts) > 1 else ""

        # Create a JSON object
        data = {
            "question_num": question_number + ".)",
            "question_text": question,
            "options": {"a": option_a, "b": option_b, "c": option_c, "d": option_d},
            "answer": answer,
            "explanation": explanation,
        }

        # return json.dumps(data, ensure_ascii=False, indent=2)
        return data

    def extract_questions(cleaned_html):
        # Split the content into individual question blocks
        question_blocks = re.split(r"(?m)^(\d{1,7}\.\))", cleaned_html)[1:]

        if len(question_blocks) % 2 != 0:
            raise ValueError(
                "Malformed document: found a question number without a "
                f"following question body near {question_blocks[-1][:80]!r}. "
                "Expected format 'N.) question (a) .. (b) .. (c) .. (d) .. Ans. .. Exp: ..'."
            )

        questions = []
        for i in range(0, len(question_blocks), 2):
            question_num = question_blocks[i].strip()
            question_block = question_blocks[i + 1].strip()

            question = extract_question_data(question_num + question_block)
            questions.append(question)

        if not questions and cleaned_html.strip():
            raise ValueError(
                "No questions found: expected 'N.)' numbered questions with "
                "'(a)..(d)', 'Ans.' and 'Exp:' markers."
            )

        return questions

    def process_questions_with_elements(questions):
        for question in questions:
            # Process question text
            question_elements = backend_extract_html_elements(question["question_text"])
            question["question_elements"] = question_elements

            # Process explanation
            explanation_elements = backend_extract_html_elements(
                question["explanation"]
            )
            question["explanation_elements"] = explanation_elements

            # Process options
            options_elements = {}
            for key in question["options"]:
                option_elements = backend_extract_html_elements(
                    question["options"][key]
                )
                options_elements[key] = option_elements

            question["options_elements"] = options_elements

            # Remove old text keys
            del question["question_text"]
            del question["explanation"]
            del question["options"]

        return questions

    # change only extension of output file path to json  if not already
    if output_file_path.endswith(".docx"):
        output_file_path = output_file_path.replace(".docx", ".json")

    extra_args = ["--standalone", "--mathml", "--embed-resources"]

    html_content = pypandoc.convert_file(
        source_file=input_file_path, to="html5", format="docx", extra_args=extra_args
    )

    # Clean the HTML content
    cleaned_html = backend_clean_html(html_content)

    # Extract questions from the cleaned HTML content
    questions = extract_questions(cleaned_html)

    # Round-trip through JSON serialization (normalizes whitespace/entities)
    # using a unique temp file — safe for parallel runs.
    fd, temp_json_file = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as json_file:
            json.dump(questions, json_file, ensure_ascii=False, indent=4)

        with open(temp_json_file, "r", encoding="utf-8") as json_file:
            questions = json.load(json_file)

        # Process the questions to maintain sequence and convert elements
        processed_questions = process_questions_with_elements(questions)
    finally:
        if os.path.exists(temp_json_file):
            os.remove(temp_json_file)

    # Save the final questions to a JSON file
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json.dump(processed_questions, json_file, ensure_ascii=False, indent=4)

    print(
        f"Questions with images, tables, and math formulas have been successfully processed and saved to {output_file_path}"
    )
    return 0


def convert_json_to_docx(input_file_path, output_file_path):

    def create_html_from_json(json_data):
        html_output = "<html><body>"
        for question in json_data:
            html_output += f"{question['question_num']} "
            html_output += backend_convert_json_elements_to_html(
                question["question_elements"]
            )
            html_output += (
                "<p>(a) "
                + backend_convert_json_elements_to_html(
                    question["options_elements"]["a"]
                )
                + "</p>"
            )
            html_output += (
                "<p>(b) "
                + backend_convert_json_elements_to_html(
                    question["options_elements"]["b"]
                )
                + "</p>"
            )
            html_output += (
                "<p>(c) "
                + backend_convert_json_elements_to_html(
                    question["options_elements"]["c"]
                )
                + "</p>"
            )
            html_output += (
                "<p>(d) "
                + backend_convert_json_elements_to_html(
                    question["options_elements"]["d"]
                )
                + "</p>"
            )
            html_output += f"<p>Ans. {question['answer']}</p>"
            html_output += (
                "<p>Exp: "
                + backend_convert_json_elements_to_html(
                    question["explanation_elements"]
                )
                + "</p>"
            )
        html_output += "</body></html>"
        return html_output

    if not input_file_path.endswith(".json"):
        return 0

    # replace  extension of output file to docx if  not alread
    if output_file_path.endswith(".json"):
        output_file_path = output_file_path.replace(".json", ".docx")

    # Load the JSON data
    with open(input_file_path, "r", encoding="utf-8", errors="ignore") as json_file:
        questions = json.load(json_file)

    # Create HTML content from JSON data
    html_content = create_html_from_json(questions)

    # Use unique temp files — safe for parallel runs, no repo pollution.
    fd_html, output_html_path = tempfile.mkstemp(suffix=".html")
    fd_docx, temp_output_docx_file = tempfile.mkstemp(suffix=".docx")
    os.close(fd_html)
    os.close(fd_docx)
    try:
        with open(output_html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        extra_args = [
            "--standalone",
            # '--mathml',
            # '--embed-resources'
        ]

        pypandoc.convert_file(
            source_file=output_html_path,
            outputfile=temp_output_docx_file,
            to="docx",
            format="html",
            extra_args=extra_args,
        )

        update_font_style_in_docx(temp_output_docx_file, output_file_path)
    finally:
        for p in (temp_output_docx_file, output_html_path):
            if os.path.exists(p):
                os.remove(p)

    print(f"DOCX file has been successfully created and saved to {output_file_path}")
    return 0
