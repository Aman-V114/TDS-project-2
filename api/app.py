from flask import Flask, request, jsonify
import os

from utils.question_matching import find_similar_question
from utils.openai_api import extract_parameters
from utils.solution_functions import functions_dict
from utils.file_process import unzip_folder


tmp_dir = "tmp_uploads"
os.makedirs(tmp_dir, exist_ok=True)

app = Flask(__name__)


@app.route("/")
def fun():
    return "works"


@app.route("/api/", methods=["POST"])
def process_file():
    question = request.form.get("question")  # Get the question from the form data
    file = request.files.get("file")  # Get the uploaded file (optional)

    # Handle the file processing if file is present


    matched_function, matched_description, matched_files = find_similar_question(
        question
    )  # Function to compare using cosine similarity

    if file:
        # this will make sure that the file is saved in the tmp_uploads folder
        # and the name of the files are exactly the same as the one in the questions.json
        unzip_folder(file, tmp_dir, matched_files) 
        pass

    parameters = extract_parameters(
        str(question)
    )  # Function to call OpenAI API and extract parameters
    
    solution_function = functions_dict.get(
        str(matched_function), lambda parameters: "No matching function found"
    )  # the solutions functions name is same as in questions.json

    answer = solution_function(matched_function, parameters)

    # Return the answer in JSON format
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
