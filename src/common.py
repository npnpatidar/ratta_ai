"""Shared helpers — single canonical copy.

Extracted verbatim from ratta_functions.py / docx2html.py to remove
duplicated import blocks and duplicated utility implementations.
Pipeline modules should import from here instead of each other
(avoids ratta_functions <-> docx2html circular import).
"""

import glob
import json
import logging
import os
import shutil
import yaml

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT

FONT_NAME = "Sahitya"
FONT_SIZE = 12


def setup_logger(log_file="process.log"):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def writeLog(message):
    with open("process.log", "a") as f:
        f.write("\n")
        f.write(str(message))


def process_folder_for_given_function(
    input_folder, output_folder, process_function, file_or_folder="files"
):
    """Recursively apply process_function, preserving folder structure."""
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


def append_to_json_file(existing_file, new_entries_list):
    is_new_entry = False
    directory = os.path.dirname(existing_file)
    if not os.path.exists(directory) and directory != "":
        os.makedirs(directory)
    if not os.path.exists(existing_file):
        with open(existing_file, "w") as f:
            f.write("[]")
    try:
        with open(existing_file, "r+", encoding="utf-8") as file:
            existing_data = json.load(file)
            for entry in new_entries_list:
                if entry not in existing_data:
                    existing_data.append(entry)
                    is_new_entry = True
            file.seek(0)
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
            file.truncate()
    except FileNotFoundError:
        with open(existing_file, "w", encoding="utf-8") as file:
            json.dump(new_entries_list, file, ensure_ascii=False, indent=4)
    finally:
        return is_new_entry


def backend_folder_to_json(folder_path, include_files=False):
    if not os.path.isdir(folder_path):
        raise ValueError(f"{folder_path} is not a directory")
    result = {"Folder": os.path.basename(folder_path)}
    children = []
    entries = sorted(os.listdir(folder_path), key=lambda x: x.lower())
    for entry in entries:
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            children.append(backend_folder_to_json(full_path, include_files))
        elif include_files:
            children.append({"File": entry})
    if children:
        result["Children"] = children
    return result


def save_folder_structure_into_yaml(folder_path, output_folder, include_files=False):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    data = backend_folder_to_json(folder_path, include_files)
    json_file_path = os.path.join(output_folder, "folder_structure.json")
    yaml_file_path = os.path.join(output_folder, "folder_structure.yaml")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(yaml_file_path, "w") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            indent=8,
            default_flow_style=False,
            sort_keys=False,
        )


def backend_create_folders_and_files(folder_structure, parent_path):
    folder_name = folder_structure["Folder"]
    current_path = os.path.join(parent_path, folder_name)
    if not os.path.exists(current_path):
        os.makedirs(current_path)
        print("created folder: ", current_path)
    if "Children" in folder_structure:
        for child in folder_structure["Children"]:
            if "File" in child:
                pass
            else:
                backend_create_folders_and_files(child, current_path)


def create_folder_structure_from_yaml(yaml_file, output_folder):
    with open(yaml_file, "r") as file:
        folder_structure = yaml.safe_load(file)
    backend_create_folders_and_files(folder_structure, output_folder)


def write_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_yaml(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            indent=8,
            default_flow_style=False,
            sort_keys=False,
        )
        f.write("\n")


def combine_json_files(folder_path, output_file):
    combined_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                combined_data.extend(json.load(f))
    with open(output_file, "w", encoding="utf-8") as out_file:
        json.dump(combined_data, out_file, ensure_ascii=False, indent=4)
    print(f"Combined JSON data saved to '{output_file}'")


# ---- DOCX styling (canonical: per-cell border from ratta_functions,
#      grapheme-aware width from docx2html) ----
def set_font(paragraph, font_name=FONT_NAME, font_size=FONT_SIZE):
    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size)
        rPr = run._element.get_or_add_rPr()
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:ascii"), font_name)
        rFonts.set(qn("w:hAnsi"), font_name)
        rFonts.set(qn("w:eastAsia"), font_name)
        rFonts.set(qn("w:cs"), font_name)
        rPr.append(rFonts)


def set_cell_border(cell):
    tc = cell._element
    tcPr = tc.get_or_add_tcPr()
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


def set_cell_borders_for_doc(doc):
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                set_cell_border(cell)


def get_max_column_width(table, col_idx):
    max_width = 0
    for row in table.rows:
        cell = row.cells[col_idx]
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                max_width = max(max_width, len(run.text))
    return max_width


def get_max_column_width_hindi(table, col_idx):
    from indicparser import graphemeParser

    max_width = 0
    for row in table.rows:
        cell = row.cells[col_idx]
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                max_width = max(
                    max_width, len(graphemeParser("hindi").process(run.text))
                )
    return max_width


def set_column_widths(table, hindi_aware=False, max_chars=40):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for col_idx in range(len(table.columns)):
        if hindi_aware:
            max_width = get_max_column_width_hindi(table, col_idx)
        else:
            max_width = get_max_column_width(table, col_idx)
        max_width = min(max_width, max_chars)
        table.columns[col_idx].width = Inches(max_width * 0.10)


def set_column_widths_auto(doc):
    for table in doc.tables:
        for column in table.columns:
            for cell in column.cells:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                tcW = tcPr.get_or_add_tcW()
                tcW.type = "auto"
                tcW.w = 0


def apply_ratta_style_to_doc(doc, font_name=FONT_NAME, font_size=FONT_SIZE):
    for paragraph in doc.paragraphs:
        set_font(paragraph, font_name, font_size)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    set_font(paragraph, font_name, font_size)
    set_cell_borders_for_doc(doc)
    set_column_widths_auto(doc)


def update_file_names_in_a_folder(folder_path, words_to_remove):
    for root, _dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_extension = os.path.splitext(file)
            for word_to_remove in words_to_remove:
                if word_to_remove in file_name:
                    file_name = file_name.replace(word_to_remove, "")
            new_file_path = os.path.join(root, file_name + file_extension)
            try:
                if file_path != new_file_path:
                    os.rename(file_path, new_file_path)
                    print(f"Renamed '{file}' to '{file_name + file_extension}'")
            except Exception as e:
                print(f"Failed to rename '{file}': {e}")


def iter_json_files(folder_path):
    return glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)


def cleanup_dirs(*dirs):
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)


# ---- Question helpers (canonical, moved from legacy txt pipeline) ----

def is_question_to_be_deleted(question):
    return False
    # return true if question contains word "कथन" or  "कथनों"
    # if len(question["question"].split()) > 40:
    # if not (('\n' in question['question']) and ("सुमेल" not in question['question'] or "सूची-" not in question['question'])):
    # #     if ("कथन" in question['question'] or "कथनों" in question['question']) and question['question'].count('\n') >= 2:
    if "\n" in question['question']:  # delete if any there is a new line character
        # if   not ("सुमेल"  in question['question'] and  "सूची-"  in question['question']  ) :
        if not ("सुमेलित क" in question['question'] or "सुमेलित न" in question['question'] or question['question'].count('सूची') >= 2):
            return True
    return False

def jaccard_similarity(string1, string2):
    set1 = set(string1.split())
    set2 = set(string2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    similarity = intersection / union if union > 0 else 0
    return similarity

def questionString(q1):
    return f"{q1['question']}\n(a) {q1['option_a']}\n(b) {q1['option_b']}\n(c) {q1['option_c']}\n(d) {q1['option_d']}\nAns. {q1['answer']}\nExp: {q1['explanation']}\n"

def make_json_readable(json_file_path, text_file_path):
    # Read complete file as single string
    with open(json_file_path, 'r') as file:
        data = file.read()

    # Remove square brackets [] and curly braces {}
    cleaned_text1 = re.sub(r'[\[\]{}]', '', data)

    # Remove all occurrences of "Children"
    cleaned_text2 = re.sub(r'"Children":', '', cleaned_text1)

    # Remove lines containing the word "length"
    cleaned_text3 = '\n'.join(
        line for line in cleaned_text2.split('\n') if 'length' not in line)

    # Remove lines containing only a comma
    cleaned_text4 = re.sub(r'^\s*,\s*$', '', cleaned_text3, flags=re.MULTILINE)

    # Remove specific pattern: comma + newline + any number of spaces + double quote
    # cleaned_text5 = re.sub(r',\n\s*"(?!\w)', '', cleaned_text4,  flags=re.MULTILINE)
    # cleaned_text5 = re.sub(r',\s*"\w+":', ', ', cleaned_text4)
    cleaned_text5 = re.sub(r'\n\s*"Total Questions":', ' "T":', cleaned_text4)
    cleaned_text6 = re.sub(r'\n\s*"No Explanation":', ' "N":', cleaned_text5)
    cleaned_text7 = re.sub(
        r'\n\s*"Percent NO Explanation":', ' "P":', cleaned_text6)
    cleaned_text8 = re.sub(r'\n\s*\n', '\n', cleaned_text7)
    cleaned_text9 = re.sub(r'.json", "T":', ' - ', cleaned_text8)
    cleaned_text10 = re.sub(r'", "T":', ' = ', cleaned_text9)
    cleaned_text11 = re.sub(r'"P":', '', cleaned_text10)
    cleaned_text12 = re.sub(r'"N":', '', cleaned_text11)
    cleaned_text13 = re.sub(r'"', '', cleaned_text12)

    # Write cleaned text to text file
    with open(text_file_path, 'w') as file:
        file.write(cleaned_text13)
