import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image  # Still needed for image validation if desired

def process_uploaded_file(file_path):
    """
    Process any uploaded file. Extracts ZIP files, copies all other files.
    Returns the directory where files are extracted or saved and a list of file names.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if the file is a ZIP file
    if zipfile.is_zipfile(file_path):
        # Handle ZIP file
        return _unzip_file(file_path)
    else:
        # Handle any other file type
        file_extension = file_path.suffix.lower().lstrip('.')
        
        # Create directory based on file extension
        base_tmp_dir = Path(f"tmp_uploads/{file_extension}")
        os.makedirs(base_tmp_dir, exist_ok=True)
        
        # Save the file
        saved_file_path = base_tmp_dir / file_path.name
        shutil.copy2(file_path, saved_file_path)
        
        return str(base_tmp_dir), [file_path.name]

def _unzip_file(zip_path):
    """
    Helper function to extract a ZIP file.
    """
    # Create a temporary directory inside tmp_uploads
    base_tmp_dir = Path("tmp_uploads/zips")
    os.makedirs(base_tmp_dir, exist_ok=True)
    extract_to = Path(tempfile.mkdtemp(dir=base_tmp_dir))

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
        extracted_files = zip_ref.namelist()

    # Return the directory where files are extracted and the list of file names
    return str(extract_to), extracted_files