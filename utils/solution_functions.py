import requests
import subprocess
import hashlib
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import zipfile
import pandas as pd
import os


def vs_code_version():
    return """
    Version:          Code 1.98.2 (ddc367ed5c8936efe395cffeec279b04ffd7db78, 2025-03-12T13:32:45.399Z)
    OS Version:       Linux x64 6.12.15-200.fc41.x86_64
    CPUs:             11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz (8 x 1300)
    Memory (System):  7.40GB (3.72GB free)
    Load (avg):       3, 2, 2
    VM:               0%
    Screen Reader:    no
    Process Argv:     --crash-reporter-id 80b4d7e7-0056-4767-b601-6fcdbec0b54d
    GPU Status:       2d_canvas:                              enabled
                    canvas_oop_rasterization:               enabled_on
                    direct_rendering_display_compositor:    disabled_off_ok
                    gpu_compositing:                        enabled
                    multiple_raster_threads:                enabled_on
                    opengl:                                 enabled_on
                    rasterization:                          enabled
                    raw_draw:                               disabled_off_ok
                    skia_graphite:                          disabled_off
                    video_decode:                           enabled
                    video_encode:                           disabled_software
                    vulkan:                                 disabled_off
                    webgl:                                  enabled
                    webgl2:                                 enabled
                    webgpu:                                 disabled_off
                    webnn:                                  disabled_off

    CPU %	Mem MB	   PID	Process
        2	   189	 18772	code main
        0	    45	 18800	   zygote
        2	   121	 19189	     gpu-process
        0	    45	 18801	   zygote
        0	     8	 18825	     zygote
        0	    61	 19199	   utility-network-service
        0	   106	 20078	ptyHost
        2	   114	 20116	extensionHost [1]
    21	   114	 20279	shared-process
        0	     0	 20778	     /usr/bin/zsh -i -l -c '/usr/share/code/code'  -p '"0c1d701e5812" + JSON.stringify(process.env) + "0c1d701e5812"'
        0	    98	 20294	fileWatcher [1]

    Workspace Stats:
    |  Window (● solutions.py - tdsproj2 - python - Visual Studio Code)
    |    Folder (tdsproj2): 6878 files
    |      File types: py(3311) pyc(876) pyi(295) so(67) f90(60) txt(41) typed(36)
    |                  csv(31) h(28) f(23)
    |      Conf files:
    """

def make_http_requests_with_uv(arguments):
    url = "https://httpbin.org/get"
    params = {"email": "23f2005217@ds.study.iitm.ac.in"}
    url, params = arguments["url"], arguments["params"]
    response = requests.get(url, params=params)
    return response.json()

def run_command_with_npx(arguments):
    filePath, prettier_version, hash_algo, use_npx = (
        "README.md",
        "3.4.2",
        "sha256",
        True,
    )
    filePath, prettier_version, hash_algo, use_npx = (
        arguments["filePath"],
        arguments["prettier_version"],
        arguments["hash_algo"],
        arguments["use_npx"],
    )
    prettier_cmd = (
        ["npx", "-y", f"prettier@{prettier_version}", filePath]
        if use_npx
        else ["prettier", filePath]
    )

    try:
        prettier_process = subprocess.run(
            prettier_cmd, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running Prettier:", e)
        return None

    formatted_content = prettier_process.stdout.encode()

    try:
        hasher = hashlib.new(hash_algo)
        hasher.update(formatted_content)
        return hasher.hexdigest()
    except ValueError:
        print(f"Invalid hash algorithm: {hash_algo}")
        return None

def use_google_sheets(rows=100, cols=100, start=15, step=12, extract_rows=1, extract_cols=10):
    matrix = np.arange(start, start + (rows * cols * step), step).reshape(rows, cols)

    extracted_values = matrix[:extract_rows, :extract_cols]

    return np.sum(extracted_values)

def calculate_spreadsheet_formula(formula: str, type: str) -> str:
    try:
        if formula.startswith("="):
            formula = formula[1:]

        if "SEQUENCE" in formula and type == "google_sheets":
            # Example: SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 5, 2), 1, 10))
            sequence_pattern = r"SEQUENCE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)"
            match = re.search(sequence_pattern, formula)

            if match:
                rows = int(match.group(1))
                cols = int(match.group(2))
                start = int(match.group(3))
                step = int(match.group(4))

                # Generate the sequence
                sequence = []
                value = start
                for _ in range(rows):
                    row = []
                    for _ in range(cols):
                        row.append(value)
                        value += step
                    sequence.append(row)

                # Check for ARRAY_CONSTRAIN
                constrain_pattern = r"ARRAY_CONSTRAIN\([^,]+,\s*(\d+),\s*(\d+)\)"
                constrain_match = re.search(constrain_pattern, formula)

                if constrain_match:
                    constrain_rows = int(constrain_match.group(1))
                    constrain_cols = int(constrain_match.group(2))

                    # Apply constraints
                    constrained = []
                    for i in range(min(constrain_rows, len(sequence))):
                        row = sequence[i][:constrain_cols]
                        constrained.extend(row)

                    if "SUM(" in formula:
                        return str(sum(constrained))

        elif "SORTBY" in formula and type == "excel":
            # Example: SUM(TAKE(SORTBY({1,10,12,4,6,8,9,13,6,15,14,15,2,13,0,3}, {10,9,13,2,11,8,16,14,7,15,5,4,6,1,3,12}), 1, 6))

            # Extract the arrays from SORTBY
            arrays_pattern = r"SORTBY\(\{([^}]+)\},\s*\{([^}]+)\}\)"
            arrays_match = re.search(arrays_pattern, formula)

            if arrays_match:
                values = [int(x.strip()) for x in arrays_match.group(1).split(",")]
                sort_keys = [int(x.strip()) for x in arrays_match.group(2).split(",")]

                # Sort the values based on sort_keys
                sorted_pairs = sorted(zip(values, sort_keys), key=lambda x: x[1])
                sorted_values = [pair[0] for pair in sorted_pairs]

                # Check for TAKE
                take_pattern = r"TAKE\([^,]+,\s*(\d+),\s*(\d+)\)"
                take_match = re.search(take_pattern, formula)

                if take_match:
                    take_start = int(take_match.group(1))
                    take_count = int(take_match.group(2))

                    # Apply TAKE function
                    taken = sorted_values[take_start - 1 : take_start - 1 + take_count]

                    # Check for SUM
                    if "SUM(" in formula:
                        return str(sum(taken))

        return "Could not parse the formula or unsupported formula type"

    except Exception as e:
        return f"Error calculating spreadsheet formula: {str(e)}"

def use_excel(values=None, sort_keys=None, num_rows=1, num_elements=9):
    if values is None:
        values = np.array([13, 12, 0, 14, 2, 12, 9, 15, 1, 7, 3, 10, 9, 15, 2, 0])
    if sort_keys is None:
        sort_keys = np.array([10, 9, 13, 2, 11, 8, 16, 14, 7, 15, 5, 4, 6, 1, 3, 12])

    sorted_values = values[np.argsort(sort_keys)]
    return np.sum(sorted_values[:num_elements])


def use_devtools(html=None, input_name=None):
    if html is None:
        html = '<input type="hidden" name="secret" value="12345">'
    if input_name is None:
        input_name = "secret"

    soup = BeautifulSoup(html, "html.parser")
    hidden_input = soup.find("input", {"type": "hidden", "name": input_name})

    return hidden_input["value"] if hidden_input else None


def count_wednesdays(start_date="1990-04-08", end_date="2008-09-29", weekday=2):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    count = sum(
        1
        for _ in range((end - start).days + 1)
        if (start + timedelta(_)).weekday() == weekday
    )
    return count


def extract_csv_from_a_zip(
    zip_path,
    extract_to="extracted_files",
    csv_filename="extract.csv",
    column_name="answer",
):
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    csv_path = os.path.join(extract_to, csv_filename)

    if not os.path.exists(csv_path):
        for root, _, files in os.walk(extract_to):
            for file in files:
                if file.lower().endswith(".csv"):
                    csv_path = os.path.join(root, file)
                    break

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if column_name in df.columns:
            return ", ".join(map(str, df[column_name].dropna().tolist()))

    return ""


def use_json():
    return ""


def multi_cursor_edits_to_convert_to_json():
    return ""


def css_selectors():
    return ""


def process_files_with_different_encodings():
    return ""


def use_github():
    return ""


def replace_across_files():
    return ""


def list_files_and_attributes():
    return ""


def move_and_rename_files():
    return ""


def compare_files():
    return ""


def sql_ticket_sales():
    return ""


def write_documentation_in_markdown():
    return ""


def compress_an_image():
    return ""


def host_your_portfolio_on_github_pages():
    return ""


def use_google_colab():
    return ""


def use_an_image_library_in_google_colab():
    return ""


def deploy_a_python_api_to_vercel():
    return ""


def create_a_github_action():
    return ""


def push_an_image_to_docker_hub():
    return ""


def write_a_fastapi_server_to_serve_data():
    return ""


def run_a_local_llm_with_llamafile():
    return ""


def llm_sentiment_analysis():
    return ""


def llm_token_cost():
    return ""


def generate_addresses_with_llms():
    return ""


def llm_vision():
    return ""


def llm_embeddings():
    return ""


def embedding_similarity():
    return ""


def vector_databases():
    return ""


def function_calling():
    return ""


def get_an_llm_to_say_yes():
    return ""


def import_html_to_google_sheets():
    return ""


def scrape_imdb_movies():
    return ""


def wikipedia_outline():
    return ""


def scrape_the_bbc_weather_api():
    return ""


def find_the_bounding_box_of_a_city():
    return ""


def search_hacker_news():
    return ""


def find_newest_github_user():
    return ""


def create_a_scheduled_github_action():
    return ""


def extract_tables_from_pdf():
    return ""


def convert_a_pdf_to_markdown():
    return ""

def clean_up_excel_sales_data(file_path):
    # Load the dataset
    df = pd.read_excel(file_path)

    # Get unique city names dynamically
    unique_cities = df["city"].unique()

    # Standardize city names using fuzzy matching
    def standardize_city(city_name):
        match, score, _ = process.extractOne(city_name, unique_cities, scorer=fuzz.ratio)
        return match if score > 80 else city_name  # Use match if confidence is high

    df["city"] = df["city"].apply(standardize_city)

    # Filter for "Ball" sales with at least 177 units
    filtered_df = df[(df["product"] == "Ball") & (df["sales"] >= 177)]

    # Aggregate sales by city
    aggregated_sales = filtered_df.groupby("city")["sales"].sum().reset_index()

    # Extract total sales in Delhi
    delhi_sales = aggregated_sales.loc[aggregated_sales["city"].str.lower() == "delhi", "sales"].sum()

    return {"Delhi_sales": int(delhi_sales)}

def clean_up_student_marks(file_path):
    # Load the JSON file
    with open(file_path, "r") as file:
        data = json.load(file)

    # Extract sales values, handling missing or invalid data
    total_sales = sum(entry.get("sales", 0) for entry in data if isinstance(entry.get("sales"), (int, float)))

    return {"total_sales": total_sales}


def parse_apache_log_line(line):
    """ Extracts key fields from an Apache log entry. """
    log_pattern = re.compile(
        r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d+) \S+ ".*" ".*"'
    )
    match = log_pattern.match(line)
    
    if not match:
        return None
    
    log_data = match.groupdict()
    log_data["status"] = int(log_data["status"])
    
    # Convert timestamp format
    timestamp_str = log_data["timestamp"].split()[0]  # Remove timezone
    log_data["datetime"] = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S")
    
    return log_data

def apache_log_requests(file_path):
    """ Processes a gzipped Apache log file and counts qualifying GET requests. """
    successful_requests = 0

    with gzip.open(file_path, "rt", encoding="utf-8") as file:
        for line in file:
            log_data = parse_apache_log_line(line)
            if not log_data:
                continue
            
            # Extract components
            request_time = log_data["datetime"]
            is_friday = request_time.weekday() == 4  # 4 = Friday
            is_in_time_window = 3 <= request_time.hour < 20
            is_successful = 200 <= log_data["status"] < 300
            is_get_request = log_data["method"] == "GET"
            is_tamilmp3_page = log_data["url"].startswith("/tamilmp3/")
            
            if is_friday and is_in_time_window and is_successful and is_get_request and is_tamilmp3_page:
                successful_requests += 1

    return {"successful_tamilmp3_get_requests": successful_requests}


def apache_log_downloads():
    return ""


def clean_up_sales_data():
    return ""


def parse_partial_json():
    return ""


def extract_nested_json_keys():
    return ""


def duckdb_social_media_interactions():
    return ""


def transcribe_a_youtube_video():
    return ""


def reconstruct_an_image(image_path=None, mapping=None, grid_size=(5, 5), output_path="reconstructed.png"):
    if image_path is None or mapping is None:
        return None  # Return None if required inputs are missing

    img = Image.open(image_path)
    width, height = img.size
    piece_width = width // grid_size[1]
    piece_height = height // grid_size[0]

    reconstructed = Image.new("RGB", (width, height))

    for orig_row, orig_col, scr_row, scr_col in mapping:
        left = scr_col * piece_width
        upper = scr_row * piece_height
        piece = img.crop((left, upper, left + piece_width, upper + piece_height))

        left = orig_col * piece_width
        upper = orig_row * piece_height
        reconstructed.paste(piece, (left, upper))

    reconstructed.save(output_path)
    return output_path  # Return the output path


functions_dict = {
    "vs_code_version": vs_code_version,
    "make_http_requests_with_uv": make_http_requests_with_uv,
    "run_command_with_npx": run_command_with_npx,
    "use_google_sheets": use_google_sheets,
    "use_excel": use_excel,
    "use_devtools": use_devtools,
    "count_wednesdays": count_wednesdays,
    "extract_csv_from_a_zip": extract_csv_from_a_zip,
    "use_json": use_json,
    "multi_cursor_edits_to_convert_to_json": multi_cursor_edits_to_convert_to_json,
    "css_selectors": css_selectors,
    "process_files_with_different_encodings": process_files_with_different_encodings,
    "use_github": use_github,
    "replace_across_files": replace_across_files,
    "list_files_and_attributes": list_files_and_attributes,
    "move_and_rename_files": move_and_rename_files,
    "compare_files": compare_files,
    "sql_ticket_sales": sql_ticket_sales,
    "write_documentation_in_markdown": write_documentation_in_markdown,
    "compress_an_image": compress_an_image,
    "host_your_portfolio_on_github_pages": host_your_portfolio_on_github_pages,
    "use_google_colab": use_google_colab,
    "use_an_image_library_in_google_colab": use_an_image_library_in_google_colab,
    "deploy_a_python_api_to_vercel": deploy_a_python_api_to_vercel,
    "create_a_github_action": create_a_github_action,
    "push_an_image_to_docker_hub": push_an_image_to_docker_hub,
    "write_a_fastapi_server_to_serve_data": write_a_fastapi_server_to_serve_data,
    "run_a_local_llm_with_llamafile": run_a_local_llm_with_llamafile,
    "llm_sentiment_analysis": llm_sentiment_analysis,
    "llm_token_cost": llm_token_cost,
    "generate_addresses_with_llms": generate_addresses_with_llms,
    "llm_vision": llm_vision,
    "llm_embeddings": llm_embeddings,
    "embedding_similarity": embedding_similarity,
    "vector_databases": vector_databases,
    "function_calling": function_calling,
    "get_an_llm_to_say_yes": get_an_llm_to_say_yes,
    "import_html_to_google_sheets": import_html_to_google_sheets,
    "scrape_imdb_movies": scrape_imdb_movies,
    "wikipedia_outline": wikipedia_outline,
    "scrape_the_bbc_weather_api": scrape_the_bbc_weather_api,
    "find_the_bounding_box_of_a_city": find_the_bounding_box_of_a_city,
    "search_hacker_news": search_hacker_news,
    "find_newest_github_user": find_newest_github_user,
    "create_a_scheduled_github_action": create_a_scheduled_github_action,
    "extract_tables_from_pdf": extract_tables_from_pdf,
    "convert_a_pdf_to_markdown": convert_a_pdf_to_markdown,
    "clean_up_excel_sales_data": clean_up_excel_sales_data,
    "clean_up_student_marks": clean_up_student_marks,
    "apache_log_requests": apache_log_requests,
    "apache_log_downloads": apache_log_downloads,
    "clean_up_sales_data": clean_up_sales_data,
    "parse_partial_json": parse_partial_json,
    "extract_nested_json_keys": extract_nested_json_keys,
    "duckdb_social_media_interactions": duckdb_social_media_interactions,
    "transcribe_a_youtube_video": transcribe_a_youtube_video,
    "reconstruct_an_image": reconstruct_an_image,
}
