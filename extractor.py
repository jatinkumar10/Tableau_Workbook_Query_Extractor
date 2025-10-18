# Extractor module for Tableau workbook archives

import zipfile
import os
from config import EXTRACTED_FILES_DIRECTORY

def extract_twbx(twbx_path, workbook_name):
    """
    Extract the .twb XML file from a .twbx archive.
    
    Args:
        twbx_path (str): Path to the .twbx file
        workbook_name (str): Name of the workbook for folder organization
        
    Returns:
        str: Path to the extracted .twb file
        
    Raises:
        FileNotFoundError: If .twb file is not found in the archive
        zipfile.BadZipFile: If the file is not a valid ZIP archive
    """
    print(f"📦 Extracting .twb from: {twbx_path}")
    
    # Create extracted files directory if it doesn't exist
    os.makedirs(EXTRACTED_FILES_DIRECTORY, exist_ok=True)
    
    # Create a subfolder for this workbook
    workbook_extract_dir = os.path.join(EXTRACTED_FILES_DIRECTORY, workbook_name)
    os.makedirs(workbook_extract_dir, exist_ok=True)
    
    # Extract the .twbx file (which is a ZIP archive)
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(workbook_extract_dir)
        print(f"📁 Extracted to: {workbook_extract_dir}")
    
    # Find the .twb file in the extracted contents
    twb_file_path = None
    for root, dirs, files in os.walk(workbook_extract_dir):
        for file in files:
            if file.endswith('.twb'):
                twb_file_path = os.path.join(root, file)
                break
        if twb_file_path:
            break
    
    if twb_file_path:
        print(f"✅ Found .twb file: {twb_file_path}")
        return twb_file_path
    else:
        raise FileNotFoundError(f"No .twb file found in the extracted archive: {twbx_path}")