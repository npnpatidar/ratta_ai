import json
import os
import re
from bs4 import BeautifulSoup
import pypandoc

def backend_clean_html(html):
    def backend_replace_options_in_table(match):
        table_html = match.group(0)
        table_html = re.sub(r'\(a\)', '(A)', table_html, flags=re.IGNORECASE)
        table_html = re.sub(r'\(b\)', '(B)', table_html, flags=re.IGNORECASE)
        table_html = re.sub(r'\(c\)', '(C)', table_html, flags=re.IGNORECASE)
        table_html = re.sub(r'\(d\)', '(D)', table_html, flags=re.IGNORECASE)
        return table_html

    html = re.sub(r'(<table.*?>.*?</table>)', backend_replace_options_in_table, html, flags=re.DOTALL)
    html = re.sub(r'<((?:strong|sup|sub|mark|em|u|del))><br />\s*\n</\1>', '<br />\n', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+\.\))', r'</p>\n<p>\1', html, flags=re.MULTILINE)
    html = re.sub(r'^\((a|b|c|d)\)', r'</p>\n<p>(\1)', html, flags=re.MULTILINE)
    html = re.sub(r'^Ans\.', r'</p>\n<p>Ans.', html, flags=re.MULTILINE)
    html = re.sub(r'^Exp:', "</p>\n<p>Exp:", html, flags=re.MULTILINE)
    html = re.sub(r'(?<!</p>)\n(?!<p>)', ' ', html)
    html = re.sub(r'</p>\n<p>', "\n", html, flags=re.DOTALL)
    html = re.sub(r'<br />', "\n", html, flags=re.DOTALL)
    html = re.sub(r'<strong>\s*\n\s*</strong>', "", html, flags=re.DOTALL)
    html = re.sub(r'<u>\s*\n\s*</u>', "", html, flags=re.DOTALL)
    html = re.sub(r'<em>\s*\n\s*</em>', "", html, flags=re.DOTALL)
    html = re.sub(r'<del>\s*\n\s*</del>', "", html, flags=re.DOTALL)
    html = re.sub(r'<mark>\s*\n\s*</mark>', "", html, flags=re.DOTALL)
    html = re.sub(r'&[a-z]+;', ' ', html)
    html = re.sub(r'\n<math', ' <math', html)
    html = re.sub(r'\n</math>', ' </math>\n', html)
    html = re.sub(r'</math><br/>', ' </math> ', html)
    html = re.sub(r'<body>.<p>', '<body>\n', html, flags=re.DOTALL)
    html = re.sub(r'\n\n+', '\n', html)
    html = re.sub(r'<p>', '', html)
    html = re.sub(r'</p>', '', html)
    html = re.sub(r'</body> </html>', '', html)
    return html

def backend_extract_html_elements(text):
    def parse_content(contents):
        for content in contents:
            if isinstance(content, str) or content.name in ['math', 'strong', 'em', 'u', 'del', 'mark', 'sub', 'sup']:
                content_str = content if isinstance(content, str) else str(content)
                if elements and elements[-1]['type'] == 'text':
                    elements[-1]['content'] += content_str
                else:
                    elements.append({'type': 'text', 'content': content_str})
            elif content.name == 'img':
                elements.append({'type': 'image', 'content': ("<br/>" + str(content))})
            elif content.name == 'table':
                elements.append({'type': 'table', 'content': backend_convert_table_to_json(str(content))})
            else:
                parse_content(content.contents)

    soup = BeautifulSoup(text, 'html.parser')
    elements = []
    parse_content(soup.contents)
    return elements

def backend_convert_json_elements_to_html(elements):
    html_content = ''
    for element in elements:
        if element['type'] == 'text':
            formatted_text = element['content'].replace('\n', '<br/>')
            html_content += formatted_text
        elif element['type'] == 'image':
            html_content += element['content']
        elif element['type'] == 'table':
            html_content += backend_convert_table_from_json(element['content'])
    html_content = html_content.replace('</math><br/>', '</math> ')
    return html_content

def backend_convert_table_from_json(table_json):
    table_html = '<table border="1">'
    for row in table_json:
        table_html += '<tr>'
        for cell in row:
            table_html += '<td>'
            if isinstance(cell, list):
                table_html += backend_convert_table_from_json(cell)
            elif isinstance(cell, dict) and 'type' in cell:
                table_html += backend_convert_json_elements_to_html([cell])
            else:
                table_html += str(cell).replace('\n', '<br/>')
            table_html += '</td>'
        table_html += '</tr>'
    table_html += '</table>'
    return table_html

def backend_convert_table_to_json(table_html):
    soup = BeautifulSoup(table_html, 'html.parser')
    table = []
    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_content = []
        for cell in cells:
            cell_html = str(cell).replace('<td>', '').replace('</td>', '').replace('<th>', '').replace('</th>', '')
            row_content.append(cell_html)
        table.append(row_content)
    return table

def convert_docx_to_json(input_file_path, output_file_path):
    def extract_question_data(input_text):
        parts = input_text.split("\nExp:")
        explanation = parts[1].strip() if len(parts) > 1 else ""
        parts = parts[0].split("\nAns.")
        answer = parts[1].strip() if len(parts) > 1 else ""
        options_text = parts[0]
        parts = options_text.rsplit("\n(d)", 1)
        option_d = parts[1].strip() if len(parts) > 1 else ""
        parts = parts[0].rsplit("\n(c)", 1)
        option_c = parts[1].strip() if len(parts) > 1 else ""
        parts = parts[0].rsplit("\n(b)", 1)
        option_b = parts[1].strip() if len(parts) > 1 else ""
        parts = parts[0].rsplit("\n(a)", 1)
        option_a = parts[1].strip() if len(parts) > 1 else ""
        question_text = parts[0].strip()
        question_parts = question_text.split(".)", 1)
        question_number = question_parts[0].strip() if len(question_parts) > 1 else ""
        question = question_parts[1].strip() if len(question_parts) > 1 else ""
        data = {
            "question_num": question_number + ".)",
            "question_text": question,
            "options": {
                "a": option_a,
                "b": option_b,
                "c": option_c,
                "d": option_d
            },
            "answer": answer,
            "explanation": explanation
        }
        return data

    def extract_questions(cleaned_html):
        question_blocks = re.split(r'(?m)^(\d{1,7}\.\))', cleaned_html)[1:]
        questions = []
        for i in range(0, len(question_blocks), 2):
            question_num = question_blocks[i].strip()
            question_block = question_blocks[i+1].strip()
            question = extract_question_data(question_num + question_block)
            questions.append(question)
        return questions

    def process_questions_with_elements(questions):
        for question in questions:
            question_elements = backend_extract_html_elements(question['question_text'])
            question['question_elements'] = question_elements
            explanation_elements = backend_extract_html_elements(question['explanation'])
            question['explanation_elements'] = explanation_elements
            options_elements = {}
            for key in question['options']:
                option_elements = backend_extract_html_elements(question['options'][key])
                options_elements[key] = option_elements
            question['options_elements'] = options_elements
            del question['question_text']
            del question['explanation']
            del question['options']
        return questions

    if output_file_path.endswith('.docx'):
        output_file_path = output_file_path.replace('.docx', '.json')

    extra_args = ['--standalone', '--mathml']
    html_content = pypandoc.convert_file(source_file=input_file_path, to='html5', format='docx', extra_args=extra_args)
    cleaned_html = backend_clean_html(html_content)
    questions = extract_questions(cleaned_html)
    temp_json_file = "temp_json_file.json"
    with open(temp_json_file, 'w', encoding='utf-8') as json_file:
        json.dump(questions, json_file, ensure_ascii=False, indent=4)
    with open(temp_json_file, 'r', encoding='utf-8') as json_file:
        questions = json.load(json_file)
    processed_questions = process_questions_with_elements(questions)
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(processed_questions, json_file, ensure_ascii=False, indent=4)
    if os.path.exists(temp_json_file):
        os.remove(temp_json_file)
    print(f"Questions with images, tables, and math formulas have been successfully processed and saved to {output_file_path}")
    return 0

def convert_json_to_docx(input_file_path, output_file_path):
    def create_html_from_json(json_data):
        html_output = '<html><body>'
        for question in json_data:
            html_output += f"{question['question_num']} "
            html_output += backend_convert_json_elements_to_html(question['question_elements'])
            html_output += '<p>(a) ' + backend_convert_json_elements_to_html(question['options_elements']['a']) + '</p>'
            html_output += '<p>(b) ' + backend_convert_json_elements_to_html(question['options_elements']['b']) + '</p>'
            html_output += '<p>(c) ' + backend_convert_json_elements_to_html(question['options_elements']['c']) + '</p>'
            html_output += '<p>(d) ' + backend_convert_json_elements_to_html(question['options_elements']['d']) + '</p>'
            html_output += '<p>Ans. ' + question['answer'] + '</p>'
            html_output += '<p>Exp: ' + backend_convert_json_elements_to_html(question['explanation_elements']) + '</p>'
        html_output += '</body></html>'
        return html_output

    with open(input_file_path, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    html_content = create_html_from_json(json_data)
    temp_html_file = "temp_html_file.html"
    with open(temp_html_file, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)
    pypandoc.convert_file(source_file=temp_html_file, to='docx', format='html', outputfile=output_file_path)
    if os.path.exists(temp_html_file):
        os.remove(temp_html_file)
    print(f"JSON data has been successfully converted to DOCX and saved to {output_file_path}")
    return 0