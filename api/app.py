from multiprocessing import process
import subprocess
from flask import Flask, request, jsonify
import os
from utils.question_matching import find_similar_question
from utils.file_process import unzip_folder
from utils.function_definations_llm import function_definitions_objects_llm
from utils.openai_api import extract_parameters
from utils.solution_functions import functions_dict

tmp_dir = "tmp_uploads"
os.makedirs(tmp_dir, exist_ok=True)

app = Flask(__name__)


SECRET_PASSWORD = os.getenv("SECRET_PASSWORD")


@app.route("/", methods=["POST"])
def process_file():
    question = request.form.get("question")
    file = request.files.get("file")  # Get the uploaded file (optional)
    file_names = []

    # Ensure tmp_dir is always assigned
    tmp_dir = "tmp_uploads"
    try:
        matched_function, matched_description = find_similar_question(question)

        if file:
            temp_dir, file_names = unzip_folder(file)
            tmp_dir = temp_dir  # Update tmp_dir if a file is uploaded
        parameters = extract_parameters(
            str(question),
            function_definitions_llm=function_definitions_objects_llm[matched_function],
        )

        solution_function = functions_dict.get(
            str(matched_function), lambda parameters: "No matching function found"
        )

        if file:
            answer = solution_function(file, *parameters)
        else:
            print(type(parameters), parameters)
            answer = solution_function(*parameters)
            print(answer)
        return jsonify({"answer": answer})
    except Exception as e:
        print(e,"this is the error")
        return jsonify({"error": str(e)}), 500


@app.route('/redeploy', methods=['GET'])
def redeploy():
    password = request.args.get('password')
    print(password)
    print(SECRET_PASSWORD)
    if password != SECRET_PASSWORD:
        return "Unauthorized", 403

    subprocess.run(["../redeploy.sh"], shell=True)
    return "Redeployment triggered!", 200


if __name__ == "__main__":
    app.run(debug=True)
