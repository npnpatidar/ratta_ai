from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import zipfile
import json
import docx2html
import random
import string
import tempfile

app = Flask(__name__)
app.config['INPUT_FOLDER'] = 'input/'
app.config['OUTPUT_FOLDER'] = 'output/'
app.config['EXTRA_FOLDER'] = 'extra/'

# Ensure folders exist
os.makedirs(app.config['INPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXTRA_FOLDER'], exist_ok=True )


@app.route('/segregate', methods=['GET', 'POST'])
def segregate_questions():
    if request.method == 'POST':
        with tempfile.TemporaryDirectory() as temp_dir:
            INPUT_FOLDER = os.path.join(temp_dir, 'input')
            OUTPUT_FOLDER = os.path.join(temp_dir, 'output')
            EXTRA_FOLDER = os.path.join(temp_dir, 'extra')
            os.makedirs(INPUT_FOLDER)
            os.makedirs(OUTPUT_FOLDER)
            os.makedirs(EXTRA_FOLDER)

            if 'file_to_segregate' not in request.files or 'guideline_file' not in request.files:
                return "No file part"
            file_to_segregate = request.files['file_to_segregate']
            guideline_file = request.files['guideline_file']
            if file_to_segregate.filename == '' or guideline_file.filename == '':
                return "No selected file"
            if file_to_segregate and guideline_file:
                filename = secure_filename(file_to_segregate.filename)
                input_file_path = os.path.join(INPUT_FOLDER, filename)
                file_to_segregate.save(input_file_path)

                # Get the guideline file
                guideline_filename = secure_filename(guideline_file.filename)
                guideline_file_path = os.path.join(INPUT_FOLDER, guideline_filename)
                guideline_file.save(guideline_file_path)

                # Debugging: Print the file path
                print(f"Guideline file path: {guideline_file_path}")

                # Read the guideline file
                guideline_json_file_path = os.path.join(INPUT_FOLDER, guideline_filename.replace(".xlsx", ".json"))
                question_map = docx2html.convert_excel_to_json(guideline_file_path, guideline_json_file_path)

                # Debugging: Print the question_map
                print(f"Question map: {question_map}")

                if question_map is None:
                    return "Failed to process the guideline file. Please check the file format and content."

                # Process the file
                docx2html.segregate_question_using_number(input_file_path, OUTPUT_FOLDER, question_map)

                # Create a ZIP file of the output
                zip_filename = filename.replace(".docx", ".zip")
                zip_path = os.path.join(EXTRA_FOLDER, zip_filename)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(OUTPUT_FOLDER):
                        for file in files:
                            zipf.write(os.path.join(root, file), file)

                return send_file(zip_path, as_attachment=True)

    return render_template('segregate.html')


@app.route('/merge_question_answer', methods=['GET', 'POST'])
def merge_question_answer():
    if request.method == 'POST':
        with tempfile.TemporaryDirectory() as temp_dir:
            INPUT_FOLDER = os.path.join(temp_dir, 'input')
            OUTPUT_FOLDER = os.path.join(temp_dir, 'output')
            EXTRA_FOLDER = os.path.join(temp_dir, 'extra')
            os.makedirs(INPUT_FOLDER)
            os.makedirs(OUTPUT_FOLDER)
            os.makedirs(EXTRA_FOLDER)
        
            if 'questions_file' not in request.files or 'answers_file' not in request.files:
                return "No file part"
            questions_file = request.files['questions_file']
            answers_file = request.files['answers_file']
            if questions_file.filename == '' or answers_file.filename == '':
                return "No selected file"
            if questions_file and answers_file:
                q_file = secure_filename(questions_file.filename)
                q_file_path = os.path.join(INPUT_FOLDER, q_file)
                questions_file.save(q_file_path)

            
                a_file = secure_filename(answers_file.filename)
                a_file_path = os.path.join(EXTRA_FOLDER, a_file)
                answers_file.save(a_file_path)

                output_file_path = os.path.join(OUTPUT_FOLDER, q_file)

                docx2html.merge_question_answer_docx(q_file_path, a_file_path, output_file_path)

                return send_file(output_file_path, as_attachment=True)

    return render_template('merge_question_answer.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
