import requests
import zipfile
import io

url = "http://127.0.0.1:5000"
questions = [
    {
        "files": None,
        "question": """Running uv run --with httpie -- https [URL] installs the Python package httpie and sends a HTTPS request to the URL.\n    Send a HTTPS request to https://httpbin.org/get with the URL encoded parameter email set to 23f2005217@ds.study.iitm.ac.in\n    What is the JSON output of the command? (Paste only the JSON body, not the headers)""",
    },
    # {
    #     "files": "tests/files/README.md",
    #     "question": "Let's make sure you know how to use npx and prettier.\n    Download . In the directory where you downloaded it, make sure it is called README.md, and run npx -y prettier@3.4.2 README.md | sha256sum.\n    What is the output of the command?",
    # },
    # {
    #     "question": "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below.\n    What is the output of code -s?"
    # }
]

for question in questions:
    data = {"question": question.get("question")}
    files = {"file": open(question.get("files"), "rb")} if question.get("files") else None
    response = requests.post(url, data=data, files=files)
    print(response.json())
