from multiprocessing import process
import subprocess
from flask import Flask, request, jsonify
import os
import json
from utils.question_matching import find_similar_question
from utils.file_process import process_uploaded_file  # Updated import
from utils.function_definations_llm import function_definitions_objects_llm
from utils.openai_api import extract_parameters
from utils.solution_functions import functions_dict

tmp_dir = "tmp_uploads"
os.makedirs(tmp_dir, exist_ok=True)

app = Flask(__name__)


@app.route("/")
def fun():
    return "works"

SECRET_PASSWORD = os.getenv("SECRET_PASSWORD")

@app.route('/redeploy', methods=['GET'])
def redeploy():
    password = request.args.get('password')
    print(password)
    print(SECRET_PASSWORD)
    if password != SECRET_PASSWORD:
        return "Unauthorized", 403

    subprocess.run(["../redeploy.sh"], shell=True)
    return "Redeployment triggered!", 200


@app.route("/", methods=["POST"])
def process_file():
    # Get the question from the form data
    question = request.form.get("question")
    file = request.files.get("file")  # Get the uploaded file (optional)
    file_names = []
    tmp_dir_local = tmp_dir  # Initialize tmp_dir_local with the global tmp_dir value

    # Handle the file processing if file is present
    matched_function, matched_description, matched_files = find_similar_question(
        question
    )  # Function to compare using cosine similarity
    print("-----------Matched Function------------\n", matched_function)
    if file:
        # Save and process the uploaded file (ZIP or image)
        file_path = os.path.join(tmp_dir, file.filename)
        file.save(file_path)  # Save the file to the tmp_uploads directory
        try:
            tmp_dir_local, file_names = process_uploaded_file(file_path)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # Extract parameters using the matched function
    parameters = extract_parameters(
        str(question),
        function_definitions_llm=function_definitions_objects_llm.get(matched_function, {}),
    )  # Function to call OpenAI API and extract parameters

    print("-----------parameters------------\n", parameters)

    # Validate if parameters were extracted successfully
    if not parameters or "arguments" not in parameters:
        return jsonify({"error": "Failed to extract parameters for the given question"}), 400

    solution_function = functions_dict.get(
        str(matched_function), lambda **kwargs: "No matching function found"
    )  # the solutions functions name is same as in questions.json

    # Parse the arguments from the parameters
    try:
        arguments = json.loads(parameters["arguments"])
    except (TypeError, json.JSONDecodeError) as e:
        return jsonify({"error": f"Invalid arguments format: {str(e)}"}), 400

    print("-----------arguments------------\n", arguments)

    # For compress_an_image, override the image_path with the actual path
    if matched_function == "compress_an_image" and file_names and tmp_dir_local:
        # Use the first uploaded image file
        actual_image_path = os.path.join(tmp_dir_local, file_names[0])
        arguments["image_path"] = actual_image_path
        print(f"Overriding image path to: {actual_image_path}")

    # Call the solution function with the extracted arguments
    try:
        answer = solution_function(**arguments)
    except Exception as e:
        return jsonify({"error": f"Error executing function: {str(e)}"}), 500

    # Return the answer in JSON format
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
