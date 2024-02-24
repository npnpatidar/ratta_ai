import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compare_questions(q1, q2, vectorizer, tfidf_matrix, threshold):
    """
    Compare two questions based on cosine similarity of their TF-IDF vectors.
    
    Parameters:
    q1 (str): The first question.
    q2 (str): The second question.
    vectorizer (TfidfVectorizer): The TF-IDF vectorizer fitted on all questions.
    tfidf_matrix (scipy.sparse.csr.csr_matrix): The TF-IDF matrix for all questions.
    threshold (float): The similarity threshold for comparison.
    
    Returns:
    bool: True if similarity is greater than or equal to threshold, else False.
    """
    # Transform the questions to TF-IDF vectors
    vectors = vectorizer.transform([q1, q2])
    
    # Compute cosine similarity between the two questions
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    
    # Compare similarity with the threshold
    return cosine_sim >= threshold

def find_duplicate(input_file, output_file, threshold):
    """
    Identify duplicate questions from a JSON file and write the results to an output file.

    Parameters:
    input_file (str): Path to the input JSON file.
    output_file (str): Path to the output file where results will be written.
    threshold (float): The similarity threshold for considering questions as duplicates.
    """
    # Load the JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Extract questions
    # questions_with_options = [item['question_elements'][0]['content'] for item in data]
    questions_with_options = []

    for item in data:
        question = item['question_elements'][0]['content']
        options = item['options_elements']
        
        # Create a formatted string for the options
        options_str = '\n'.join([f"{key}: {value[0]['content']}" for key, value in options.items()])
        
        # Combine question and options
        question_with_options = f"{question}\nOptions:\n{options_str}"
        
        # Add to the list
        questions_with_options.append(question_with_options)
    
    # Fit the TF-IDF Vectorizer on the list of questions
    vectorizer = TfidfVectorizer().fit(questions_with_options)
    
    # Transform all questions to TF-IDF vectors
    tfidf_matrix = vectorizer.transform(questions_with_options)
    
    # Identify duplicates
    duplicates = []
    num_questions = len(questions_with_options)
    
    for i in range(num_questions):
        for j in range(i + 1, num_questions):
            q1 = questions_with_options[i]
            q2 = questions_with_options[j]
            if compare_questions(q1, q2, vectorizer, tfidf_matrix, threshold):
                similarity = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix[j:j+1])[0][0]
                duplicates.append({
                    'question_num_1': data[i]['question_num'],
                    'question_1': q1,
                    'question_num_2': data[j]['question_num'],
                    'question_2': q2,
                    'similarity': similarity
                })
    
    # Write results to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(duplicates, file, ensure_ascii=False, indent=4)

# Example usage
input_file = 'similarity.json'
output_file = 'duplicates.json'
threshold = 0.8

find_duplicate(input_file, output_file, threshold)




# -----------------------------------------------------------------------------------


# import json
# import torch
# from transformers import BertTokenizer, BertModel
# from sklearn.metrics.pairwise import cosine_similarity

# # Initialize BERT model and tokenizer
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

# def get_bert_embeddings(texts, tokenizer, model):
#     """
#     Get BERT embeddings for a list of texts.

#     Parameters:
#     texts (list of str): List of texts to convert to embeddings.
#     tokenizer (BertTokenizer): BERT tokenizer.
#     model (BertModel): BERT model.

#     Returns:
#     numpy.ndarray: Array of BERT embeddings.
#     """
#     inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     embeddings = outputs.last_hidden_state.mean(dim=1).numpy()  # Use mean pooling
#     return embeddings

# def compare_questions_bert(q1, q2, tokenizer, model, threshold):
#     """
#     Compare two questions based on cosine similarity of their BERT embeddings.

#     Parameters:
#     q1 (str): The first question.
#     q2 (str): The second question.
#     tokenizer (BertTokenizer): BERT tokenizer.
#     model (BertModel): BERT model.
#     threshold (float): The similarity threshold for comparison.

#     Returns:
#     bool: True if similarity is greater than or equal to threshold, else False.
#     """
#     embeddings = get_bert_embeddings([q1, q2], tokenizer, model)
#     cosine_sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
#     return cosine_sim >= threshold

# def find_duplicate(input_file, output_file, threshold):
#     """
#     Identify duplicate questions from a JSON file and write the results to an output file.

#     Parameters:
#     input_file (str): Path to the input JSON file.
#     output_file (str): Path to the output file where results will be written.
#     threshold (float): The similarity threshold for considering questions as duplicates.
#     """
#     # Load the JSON file
#     with open(input_file, 'r', encoding='utf-8') as file:
#         data = json.load(file)
    
#     # Extract questions and their ids
#     questions = [item['question_elements'][0]['content'] for item in data]
#     question_ids = [item['question_num'] for item in data]
    
#     # Get BERT embeddings for all questions
#     embeddings = get_bert_embeddings(questions, tokenizer, model)
    
#     # Identify duplicates
#     duplicates = []
#     num_questions = len(questions)
    
#     for i in range(num_questions):
#         for j in range(i + 1, num_questions):
#             q1 = questions[i]
#             q2 = questions[j]
#             if compare_questions_bert(q1, q2, tokenizer, model, threshold):
#                 similarity = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
#                 duplicates.append({
#                     'question_num_1': question_ids[i],
#                     'question_1': q1,
#                     'question_num_2': question_ids[j],
#                     'question_2': q2,
#                     'similarity': similarity
#                 })
    
#     # Write results to the output file
#     with open(output_file, 'w', encoding='utf-8') as file:
#         json.dump(duplicates, file, ensure_ascii=False, indent=4)

# # Example usage
# input_file = 'similarity.json'
# output_file = 'duplicates.json'
# threshold = 0.5

# find_duplicate(input_file, output_file, threshold)
