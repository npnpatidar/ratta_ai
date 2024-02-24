import os
from openai import OpenAI
import docx2html
import json
import ratta_functions
import glob
import shutil
import re
from g4f.client import Client
from g4f.cookies import set_cookies_dir, read_cookie_files
from g4f.Provider import BingCreateImages, OpenaiChat, Gemini
import g4f.debug
import google.generativeai as genai

import time
import timeit

input_folder = "/home/naresh/Work/Working/input"
json_folder = "/home/naresh/Work/Working/json"
output_folder = "/home/naresh/Work/Working/output"
folder_with_duplicate = "/home/naresh/Work/Working/duplicate"

cookies_dir = os.path.join(os.path.dirname(__file__), "har_file")
set_cookies_dir(cookies_dir)
read_cookie_files(cookies_dir)
g4f_client = Client( provider=OpenaiChat)

def call_llm(user_prompt, system_prompt="",  host="", model="", json_output=False):

    if system_prompt == "":
        system_prompt = "You are a helpful assistant."

    if host == "":
        host = "groq"
    if host == "groq":
        client = OpenAI(api_key="",
                        base_url="https://api.groq.com/openai/v1")
        if model == "":
            # model ="llama3-70b-8192"
            model = "llama-3.1-70b-versatile"
    elif host == "ollama":
        client = OpenAI(api_key='http://localhost:11434/v1',
                        base_url="http://localhost:11434/v1")
        if model == "":
            # model = "llama3.1:latest"
            model = "gemma2:2b"
            # model  = "mistral-nemo:latest"
            # model = "aya:latest"
            # model = "qwen2:0.5b"
    elif host == "alma":
        client = OpenAI(
            api_key="API-KEY", base_url="")
        if model == "":
            # model  = "qwen2:0.5b"
            model = "gemma2:2b"
    elif host == "openrouter":
        client = OpenAI(api_key="",
                        base_url="https://openrouter.ai/api/v1")
        if model == "":
            model = "llama3.1"
    elif host == "g4f":
        client = Client( provider=OpenaiChat)
        model = "gpt-4o-mini"
    elif host ==" gemini":
        client = Client( provider=OpenaiChat)
        model = "gpt-4o-mini"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        if json_output == True:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
        print(response.choices[0].message.content)
        return ([1 , response.choices[0].message.content])
    except Exception as e:
        print(e)
        return ([0, " "])

def get_tag_for_question_from_ai(question, categories):

    category_prompt = ""
    i = 0
    for category in categories:
        category_prompt += str(i) + " - " + category + "\n"
        i += 1

    system_prompt = ''' Classify the given question into one of the predefined topics. Please respond with the code of the topic that best fits given question.


    TOPICS Available:
    
    ''' + category_prompt + '''

    Your response should be a JSON object like below

    Format of Expected Response:
    {
    "code":"code of the topic that best fits given question"
    }


    Example of Expected Response:

    {
    "code":6
    }
    '''
    [status1, tag1] = call_llm(system_prompt=system_prompt, user_prompt=str(
        question), host="g4f", model="llama3-70b-8192", json_output=True)

    [status2, tag2] = call_llm(system_prompt=system_prompt, user_prompt=str(
        question), host="g4f", model="mixtral-8x7b-32768", json_output=True)
    
    if status1 == 0 or status2 == 0:
        return categories[-1]
    else:
        try:
            tag1 = categories[int(str(json.loads(tag1)["code"]).split()[0])]
            tag2 = categories[int(str(json.loads(tag2)["code"]).split()[0])]
            print(tag1)
            print(tag2)
            
            if tag1 == tag2:
                return tag1
            else:
                ratta_functions.writeLog("tag1 : " + tag1 + " \ntag2 : " + tag2)
                ratta_functions.writeLog(question)
                return categories[-1]
        except Exception as e:
            print(str(e))
            return categories[-1]

def segregate_questions_using_ai(input_folder_path, output_folder_path, categories):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    temp_folder = "temporary"
    another_temp = "another_temp"
    if not os.path.exists(another_temp):
        os.makedirs(another_temp)

    ratta_functions.process_folder_for_given_function(
        input_folder_path, temp_folder, docx2html.convert_docx_to_json, "files")

    json_files = glob.glob(os.path.join(
        temp_folder, '**/*.json'), recursive=True)

    for filename in json_files:
        with open(filename, 'r') as f:
            data = json.load(f)
            for question in data:
                tag = get_tag_for_question_from_ai(question, categories)
                output_file_path = os.path.join(another_temp, tag + ".json")
                ratta_functions.append_to_json_file(
                    output_file_path, [question])
    ratta_functions.process_folder_for_given_function(
        another_temp, output_folder_path, docx2html.convert_json_to_docx, "files")

    if os.path.exists(another_temp):
        shutil.rmtree(another_temp)

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)

def testing_g4f_api():
    response = g4f_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "List out all months with days in a year.  give answer in json format"}],
        response_format={"type": "json_object"}
    )
    print(response.choices[0].message.content)
    print("\n\n\n-----------------------------------------------------------------------------------------------------------------------------")

def testing_g4f_api_stream():
    response = g4f_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "why sky is blue?"}],
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content or "", end="")

def correct_typographical_mistakes_in_question(incorrect_question):
    system_prompt = ''' The given question has some typographical mistakes in it which need to be corrected. 
            Correct the typographical mistakes in the given question. 
            Return the corrected question in JSON format as given to you.
            Keep HTML tags as it is.
            Do not touch images in the given question.
            If some questions are missing explanation then provide precise and concise explanation.
            REMEMBER JSON FORMAT SHOULD BE EXACTLY SAME AS GIVEN IN QUESTION.
            '''

    user_prompt = incorrect_question

    # Call the language model (LLM) to get the corrected question
    [status, corrected_question_str] = call_llm(system_prompt=system_prompt, user_prompt=str(
        user_prompt), host="g4f", model="mixtral-8x7b-32768", json_output=True)
    
    # Parse the corrected question from JSON string to a Python dictionary
    try:
        corrected_question = json.loads(corrected_question_str)  # Ensure it's parsed as a JSON object
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        corrected_question = {}  # or handle as required

    return corrected_question

def correct_typographical_mistakes_in_file(input_file_path, output_file_path):
    input_file_json = "input_file_json.json"
    output_file_json = "output_file_json.json"
    docx2html.convert_docx_to_json(input_file_path, input_file_json)
    with open(input_file_json, 'r') as f:
        data = json.load(f)

    corrected_data = []
    for question in data:
        corrected_question = correct_typographical_mistakes_in_question(question)
        corrected_data.append(corrected_question)


        # for question in data:
        #     corrected_question = correct_typographical_mistakes_in_question(question)
        #     data[data.index(question)] = corrected_question
    
    
    with open(output_file_json, 'w') as f:
        json.dump(corrected_data, f)

    docx2html.convert_json_to_docx(output_file_json, output_file_path)

    return 0


