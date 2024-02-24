# write a function which takes prompt as input and return openai api response
import os
from openai import OpenAI
import ratta_functions




def main():

    ratta_functions.setup_logger("process.log")
    
    # get initial idea of folder 
    # docx_folder_1 = "/home/naresh/Data/Sync_N_Laptop/RattaAI/Books/Naresh books content/20-4-24/YOUTH HINDI GENERAL/YOUTH Hindi Gen By Nisha"
    docx_hindi = "/home/naresh/Data/npnpatidar/Shared/BOOKS/Naresh books content/Edited By Naresh/Women Supervisor Everything/Women Supervisor/09 भाषा योग्यता परीक्षण- हिन्दी"
    docx_english = "/home/naresh/Data/npnpatidar/Shared/BOOKS/Naresh books content/Edited By Naresh/Women Supervisor Everything/Women Supervisor/08 Language ability test- English"
    docx_science = "/home/naresh/Data/npnpatidar/Shared/BOOKS/Naresh books content/Edited By Naresh/Women Supervisor Everything/Women Supervisor/06 सामान्य विज्ञान"
    docx_reasoning = "/home/naresh/Data/npnpatidar/Shared/BOOKS/Naresh books content/Edited By Naresh/Women Supervisor Everything/Women Supervisor/07 तार्किक ज्ञान, बौधिक क्षमता और मूल गणना"
   
    docx_complete = "/home/naresh/Work/Working/Women Supervisor Everything/Women Supervisor"
    upsc_folder = "/home/naresh/Data/Sync_N_Laptop/RattaAI/UPSC POLITY TEST/Polity APP WOrk"
    docx_rajasthan_integration = "/home/naresh/Work/Working/Rajasthan Copy/Rajasthan Integration"
    docx_test_for_ai = "/home/naresh/Work/AI/test"
    docx_moomal = "/home/naresh/Work/Working/Rajasthan Copy/मूमल ऑल राजस्थान vol 1 done by GUNJAN"
    
    docx_test ="/home/naresh/Work/Working/1st Paper/001 2nd Grade P-1 GK by Naresh/001 Geographical, Historical, Cultural and General Knowledge of Rajasthan/002 History"
    # docx_reasoning = "/home/naresh/Data/Sync_N_Laptop/RattaAI/Books/Naresh books content/20-4-24/SSC REASONING (SOLVED QUE PAPER 1997)"
     # ratta_functions.get_initial_idea_of_files_from_a_folder_recursively("/home/naresh/Work/Working/Rajasthan Copy/Rajasthan Integration/01 राजस्थान का इतिहास/Rajasthan")
    docx_input = "/home/naresh/Work/Working/input"
    docx_output = "/home/naresh/Work/Working/output"
    ratta_functions.get_initial_idea_of_files_from_a_folder_recursively(docx_input)
    ratta_functions.get_initial_idea_of_files_from_a_folder_recursively(docx_output)

# ratta_functions.update_file_names_in_a_folder()

# Final Function to run 
# docx_folder_1 = "/home/naresh/Data/npnpatidar/Shared/BOOKS/Naresh books content/Edited By Naresh/Women Supervisor Everything/Women Supervisor/03 राजस्थान पर विशेष बल के साथ भारतीय राजनीति और भारतीय अर्थशास्त्र/01 राजनीति"
    # duplicates ,  to_be_deleted = ratta_functions.final_function_for_deduplication(docx_test)
    # print( " Total duplicates = "  + str( duplicates) )
    # print( " Total to be deleted = "+ str( to_be_deleted))



    # ratta_functions.find_duplicates_in_docx_folders_save_to_different_folders("/home/naresh/Work/Working/खण्ड 'अ'  राजस्थान का भूगोल", docx_test )



    #  Get Details about folder and save it in a file
    # folder_path = "/home/naresh/Desktop/02 भारत का इतिहास"
    # output_file_path = 'output.txt'
    # ratta_functions.process_files_in_folder(folder_path, ratta_functions.details_extracted, output_file_path)

    #Create one line questions from ratta doc
    # input_file = "input.txt"
    # output_file = "oneline.txt"
    # ratta_functions.convert_to_one_line( input_file, output_file )


    # Call g4f api
    # input_file = "input.txt"
    # output_file = "output.txt"
    # ratta_functions.g4f_api( input_file, output_file )

    # Read the text file
    # file_path = "input.txt"

    # ratta_functions.g4f_api( file_path, "output.txt" )

    # Call the function and get the array of questions
    # questions_array = ratta_functions.extract_questions(file_path)

    # # Print or use the array as needed
    # for i, question in enumerate(questions_array, start=1):
    #     print(f"{i}. {question}")

    #     reformatted_question= ratta_functions.call_g4f_api("Rephrase this question without changing the format of the question: \n\n" +  question)

    #     print(reformatted_question)
    #     print ( "\n\n------------------------------------------------------------\n\n")












if __name__ == "__main__":
    main()



# from docx import Document
# from docx.shared import Pt, Cm
# from docx.oxml.ns import qn
# from docx.oxml import OxmlElement
# from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

# def format_tables(input_file, output_file):
#     try:
#         # Load the document
#         doc = Document(input_file)
#         print(f"Loaded document: {input_file}")
        
#         # Function to set full borders for a cell
#         def set_cell_border(cell):
#             tc = cell._element.tcPr
#             tc.append(OxmlElement('w:tcBorders'))
#             for border in ['top', 'left', 'bottom', 'right']:
#                 tcBorders = tc[-1]
#                 tcBorder = OxmlElement(f'w:{border}')
#                 tcBorder.set(qn('w:val'), 'single')
#                 tcBorder.set(qn('w:sz'), '4')
#                 tcBorder.set(qn('w:space'), '0')
#                 tcBorder.set(qn('w:color'), '000000')
#                 tcBorders.append(tcBorder)

#         # Function to calculate the maximum width of text in a column
#         def get_max_column_width(table, col_idx):
#             max_width = 0
#             for row in table.rows:
#                 cell = row.cells[col_idx]
#                 for paragraph in cell.paragraphs:
#                     for run in paragraph.runs:
#                         max_width = max(max_width, len(run.text))
#             return max_width

#         # Function to set the width of columns based on the widest content
#         def set_column_widths(table):
#             num_columns = len(table.columns)
#             column_widths = [get_max_column_width(table, col_idx) for col_idx in range(num_columns)]
            
#             for col_idx, width in enumerate(column_widths):
#                 table.columns[col_idx].width = Cm(width * 0.6)  # Convert character count to cm (approximate)

#         # Format all tables in the document
#         for table in doc.tables:
#             for row in table.rows:
#                 for cell in row.cells:
#                     set_cell_border(cell)

#         # Set column widths for all tables
#         for table in doc.tables:
#             set_column_widths(table)

#         # Set font for all text in the tables
#         for table in doc.tables:
#             for row in table.rows:
#                 for cell in row.cells:
#                     for paragraph in cell.paragraphs:
#                         for run in paragraph.runs:
#                             run.font.size = Pt(12)
#                             run.font.name = 'Sahitya'
#                             # Ensure the font name is set correctly
#                             rPr = run._element.get_or_add_rPr()
#                             rFonts = OxmlElement('w:rFonts')
#                             rFonts.set(qn('w:ascii'), 'Sahitya')
#                             rFonts.set(qn('w:hAnsi'), 'Sahitya')
#                             rFonts.set(qn('w:eastAsia'), 'Sahitya')
#                             rFonts.set(qn('w:cs'), 'Sahitya')
#                             rPr.append(rFonts)

#         print(f"Formatted all tables in the document")
        
#         # Save the modified document
#         doc.save(output_file)
#         print(f"Saved formatted document as: {output_file}")
    
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Example usage:
# format_tables("chauhan.docx", "tables_formatted.docx")