# import ai
import docx2html
import ratta_functions
import os


# # Example usage
# convert_docx_to_json('input.docx', 'questions.json')

# # Example usage
# convert_json_to_docx('questions.json', 'output.docx')
input_folder = "/home/naresh/Work/Working/input"
json_folder = "/home/naresh/Work/Working/json"
output_folder = "/home/naresh/Work/Working/output"
folder_with_duplicate = "/home/naresh/Work/Working/duplicate"
new_folder_to_integrate = "/home/naresh/Work/Working/new"
extra_folder = "/home/naresh/Work/Working/extra"


# test questions format

ratta_functions.process_folder_for_given_function(input_folder, json_folder, docx2html.convert_docx_to_json, 'files')
ratta_functions.process_folder_for_given_function( json_folder, output_folder, docx2html.convert_json_to_docx, 'files')

# ratta_functions.get_initial_idea_of_files_from_a_folder_recursively(input_folder)
# ratta_functions.get_initial_idea_of_files_from_a_folder_recursively(output_folder)


# find duplicates

# duplicates ,  to_be_deleted   = docx2html.final_function_to_delete_duplicate_questions(input_folder, output_folder,folder_with_duplicate)
# ratta_functions.writeLog( " Total duplicates = "  + str( duplicates) )
# ratta_functions.writeLog( " Total to be deleted = "+ str( to_be_deleted))
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(input_folder)
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(output_folder)
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(folder_with_duplicate)

guide_line_json = {
    "न्यायालय": ["न्यायालय"],
    "संयुक्त राष्ट्र संघ": ["संयुक्त राष्ट्र संघ "]
}



# segregate_question(input_folder, output_folder , guide_line_json , False)



# Integrate new folder into existing folder 

# docx2html.integrate_new_folder_into_existing_folder(input_folder, new_folder_to_integrate, output_folder)
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(input_folder)
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(output_folder)
# docx2html.get_initial_idea_of_files_from_a_folder_recursively(new_folder_to_integrate)


# find wrong format questions 

# ratta_functions.process_folder_for_given_function(input_folder, output_folder, docx2html.find_wrong_format_question,"files")




geography = [
    "विश्व",
    "भारत - परिचय",
    "भारत - राजनितिक विभाजन",
    "भारत - भौतिक विभाजन",
    "भारत - अपवाह तंत्र",
    "भारत - उद्योग",
    "भारत - कृषि",
    "भारत - उर्जा",
    "भारत - खनिज",
    "भारत - जनसंख्या",
    "भारत - जलवायु",
    "भारत - परिवहन",
    "भारत - पर्यटन",
    "भारत - आपदाए",
    "भारत - वनस्पति",
    "भारत - मिट्टियां",
    "भारत - सिंचाईं व परियोजनाएँ",
    "भारत - विविध"
]

rajasthan_geography = [
    "जिले का गठन",
    "अंतर्राष्ट्रीय सीमा",
    "क्षेत्रफ़ल",
    "जिला मुख्यालय",
    "संभाग"
]

# docx2html.get_initial_idea_of_files_from_a_folder_recursively(input_folder)

# segregate_questions_using_ai(input_folder, output_folder, rajasthan_geography)
# ratta_functions.process_folder_for_given_function(input_folder, output_folder ,  ai.correct_typographical_mistakes_in_file,"files")

# docx2html.get_initial_idea_of_files_from_a_folder_recursively(output_folder)



# Cumulative explanation for questions 

# ratta_functions.process_folder_for_given_function(input_folder, extra_folder, docx2html.get_cummulative_explanation ,"files")  
# ratta_functions.process_folder_for_given_function(extra_folder,output_folder, docx2html.convert_docx_to_markdown, "files") 
# ratta_functions.process_folder_for_given_function(output_folder,folder_with_duplicate, docx2html.convert_markdown_to_docx, "files") 
# ratta_functions.process_folder_for_given_function(extra_folder,output_folder, docx2html.update_font_style_in_docx, "files") 
# ratta_functions.process_folder_for_given_function(input_folder, output_folder, docx2html.append_extra_explanation_to_every_question_file ,"files")

# docx2html.append_extra_explanation_to_every_question_file("/home/naresh/Work/Working/input/01 अनूपगढ़.docx", "/home/naresh/Work/Working/output/01 अनूपगढ़.docx")


# docx2html.convert_excel_to_json("~/Desktop/itihas.xlsx" , "~/Desktop/itihas.json")
# docx2html.convert_json("~/Desktop/itihas.json" , "~/Desktop/itihas_1.json")



# Create folder Structure from yaml file
# yaml_file = "folder_structure.yaml"
# yaml_file = "/home/naresh/Desktop/rajasthan_geo.yaml"
# output_folder = "/home/naresh/Work/Working/RAS PRE/RAS_PRE/"
# ratta_functions.create_folder_structure_from_yaml(yaml_file, output_folder)


# Save Folder Structure into yaml file
# folder = "/home/naresh/Work/Working/RAS PRE/RAS_PRE"

# ratta_functions.save_folder_structure_into_yaml( folder, "." , include_files = False)

# docx2html.merge_question_answer_docx("/home/naresh/Work/Working/input/test.docx" ,"/home/naresh/Work/Working/extra/test.docx", "/home/naresh/Work/Working/ouput/test.docx")