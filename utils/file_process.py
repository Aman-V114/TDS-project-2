import os
import zipfile
import tempfile
from pathlib import Path
from PIL import Image  # Add this import to handle image files

def process_uploaded_file(file_path):
    """
    Process the uploaded file. Handles both ZIP files and image files.
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
        # Check if the file is an image
        try:
            with Image.open(file_path) as img:
                # Save the image to a writable directory
                base_tmp_dir = Path("tmp_uploads/images")  # Updated to use a relative path
                os.makedirs(base_tmp_dir, exist_ok=True)
                saved_image_path = base_tmp_dir / file_path.name
                img.save(saved_image_path)
                return str(base_tmp_dir), [file_path.name]
        except Exception as e:
            raise ValueError(f"The file provided is neither a valid ZIP file nor an image: {file_path}. Error: {e}")

def _unzip_file(zip_path):
    """
    Helper function to extract a ZIP file.
    """
    # Create a temporary directory inside tmp_uploads
    base_tmp_dir = Path("tmp_uploads/zips")  # Updated to use a relative path
    os.makedirs(base_tmp_dir, exist_ok=True)
    extract_to = Path(tempfile.mkdtemp(dir=base_tmp_dir))

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    # Return the directory where files are extracted and the list of file names
    return str(extract_to), zip_ref.namelist()