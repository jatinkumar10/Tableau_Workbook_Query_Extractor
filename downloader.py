# Downloader module for Tableau workbooks

import requests
import os
from config import get_tableau_auth_headers, TABLEAU_SERVER_URL, TABLEAU_SITE_ID, TABLEAU_API_VERSION, DOWNLOAD_DIRECTORY

def download_workbook(workbook_id, workbook_name):
    """
    Download a Tableau workbook in .twbx format from the server.
    
    Args:
        workbook_id (str): The ID of the workbook to download
        workbook_name (str): Name for the downloaded file
        
    Returns:
        str: Local file path of the downloaded .twbx file
        
    Raises:
        requests.RequestException: If download fails
        FileNotFoundError: If workbook not found
    """
    print(f"📥 Downloading workbook: {workbook_name} (ID: {workbook_id})")
    
    # Construct the API endpoint for workbook content
    if TABLEAU_SITE_ID:
        download_url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_API_VERSION}/sites/{TABLEAU_SITE_ID}/workbooks/{workbook_id}/content"
    else:
        download_url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_API_VERSION}/workbooks/{workbook_id}/content"
    
    # Get authentication headers
    headers = get_tableau_auth_headers()
    
    # Make the download request with REST API enforcement
    print(f"🔗 Download URL: {download_url}")
    response = requests.get(download_url, headers=headers, stream=True, allow_redirects=False)
    
    # Check for redirection to VizPortal
    if response.status_code in [301, 302, 303, 307, 308]:
        location = response.headers.get('Location', '')
        if 'vizportal' in location.lower():
            raise Exception(f"REST API blocked - redirected to VizPortal: {location}")
    
    # If redirected, follow the redirect but warn
    if response.status_code in [301, 302, 303, 307, 308]:
        print(f"⚠️ Warning: Request redirected to: {response.headers.get('Location', 'Unknown')}")
        response = requests.get(download_url, headers=headers, stream=True)
    
    # Check if request was successful
    if response.status_code == 200:
        # Create downloads directory if it doesn't exist
        os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
        
        # Define the local file path
        local_file_path = os.path.join(DOWNLOAD_DIRECTORY, f"{workbook_name}.twbx")
        
        # Save the workbook content to file
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Workbook downloaded successfully: {local_file_path}")
        print(f"📊 File size: {os.path.getsize(local_file_path)} bytes")
        
        return local_file_path
        
    elif response.status_code == 404:
        raise FileNotFoundError(f"Workbook with ID '{workbook_id}' not found on the server")
    else:
        response.raise_for_status()