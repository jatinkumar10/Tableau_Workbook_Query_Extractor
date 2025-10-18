# Configuration settings for Tableau SQL Extractor

import requests
import xml.etree.ElementTree as ET
import json
from typing import Optional, Dict, Any

# Tableau Server Configuration
TABLEAU_SERVER_URL = "ADD YOUR TABLEAU_SERVER_URL HERE"
TABLEAU_SITE_CONTENT_URL = "ADD YOUR TABLEAU_SITE_CONTENT_URL HERE"  # Content URL for authentication
TABLEAU_SITE_ID = "ADD YOUR TABLEAU_SITE_ID HERE"  # Site ID for API calls
TABLEAU_API_VERSION = "3.20"

# Authentication Configuration
TABLEAU_TOKEN_NAME = "ADD YOUR TABLEAU_TOKEN_NAME HERE"
TABLEAU_TOKEN_VALUE = "ADD YOUR TABLEAU_TOKEN_VALUE HERE"
TABLEAU_CLIENT_ID = "ADD YOUR TABLEAU_CLIENT_ID HERE"

# Username/Password Authentication (Alternative method)
TABLEAU_USERNAME = "data.cars24.com"
TABLEAU_PASSWORD = "your-password"

# Additional Authentication Parameters
TABLEAU_TIMEOUT = 30  # Request timeout in seconds
TABLEAU_VERIFY_SSL = True  # SSL certificate verification

# Local Directory Paths
DOWNLOAD_DIRECTORY = "./downloads"
EXTRACTED_FILES_DIRECTORY = "./extracted_files"
SQL_OUTPUT_DIRECTORY = "./sql_output"

# Global session token storage
TABLEAU_SESSION_TOKEN = None

def authenticate_with_tableau() -> Optional[str]:
    """
    Authenticate with Tableau Server using Personal Access Token
    Returns session token if successful, None if failed
    """
    global TABLEAU_SESSION_TOKEN
    
    print("🔐 Authenticating with Tableau Server...")
    
    # Create XML payload for Personal Access Token authentication
    credentials_xml = f"""
    <tsRequest>
        <credentials personalAccessTokenName="{TABLEAU_TOKEN_NAME}" 
                    personalAccessTokenSecret="{TABLEAU_TOKEN_VALUE}">
            <site contentUrl="{TABLEAU_SITE_CONTENT_URL}" />
        </credentials>
    </tsRequest>
    """
    
    # Also create JSON payload as alternative
    credentials_json = {
        "credentials": {
            "personalAccessTokenName": TABLEAU_TOKEN_NAME,
            "personalAccessTokenSecret": TABLEAU_TOKEN_VALUE,
            "site": {
                "contentUrl": TABLEAU_SITE_CONTENT_URL
            }
        }
    }
    
    url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_API_VERSION}/auth/signin"
    
    # Try XML first (official format)
    session_token = _try_auth_request(url, credentials_xml, "application/xml", "XML")
    
    # If XML fails, try JSON
    if not session_token:
        session_token = _try_auth_request(url, credentials_json, "application/json", "JSON")
    
    if session_token:
        TABLEAU_SESSION_TOKEN = session_token
        print("✅ Authentication successful!")
        print(f"📋 Session Token: {session_token[:20]}...")
        return session_token
    else:
        print("❌ Authentication failed")
        return None

def _try_auth_request(url: str, payload: Any, content_type: str, payload_type: str) -> Optional[str]:
    """
    Try authentication request with given payload format
    Returns session token if successful, None if failed
    """
    # Try authentication with given payload format
    
    headers = {
        "Content-Type": content_type,
        "Accept": "application/xml"
    }
    
    try:
        if content_type == "application/json":
            response = requests.post(url, json=payload, headers=headers, timeout=TABLEAU_TIMEOUT)
        else:
            response = requests.post(url, data=payload, headers=headers, timeout=TABLEAU_TIMEOUT)
        
        if response.status_code == 200:
            return _parse_auth_response(response.text)
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def _parse_auth_response(response_xml: str) -> Optional[str]:
    """
    Parse successful authentication response and extract session token
    """
    try:
        root = ET.fromstring(response_xml)
        
        # Extract session token - try with namespace first, then without
        credentials = root.find('.//{http://tableau.com/api}credentials')
        if credentials is None:
            # Try without namespace
            credentials = root.find('.//credentials')
        
        if credentials is not None:
            session_token = credentials.get('token')
            
            # Extract additional info (optional)
            site = credentials.find('{http://tableau.com/api}site')
            if site is None:
                site = credentials.find('site')
                
            user = credentials.find('{http://tableau.com/api}user')
            if user is None:
                user = credentials.find('user')
            
            return session_token
        else:
            print("❌ No credentials found in response")
            print(f"Available elements: {[elem.tag for elem in root.iter()]}")
            return None
            
    except ET.ParseError as e:
        print(f"❌ Failed to parse XML response: {e}")
        return None

def get_tableau_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for Tableau API requests
    Automatically authenticates if no session token exists
    """
    global TABLEAU_SESSION_TOKEN
    
    # If no session token, authenticate first
    if not TABLEAU_SESSION_TOKEN:
        authenticate_with_tableau()
    
    if TABLEAU_SESSION_TOKEN:
        return {
            "X-Tableau-Auth": TABLEAU_SESSION_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/xml",
            "User-Agent": "Tableau-REST-API-Client/1.0",
            "X-Requested-With": "XMLHttpRequest",
            "X-Tableau-API-Version": TABLEAU_API_VERSION
        }
    else:
        raise Exception("Failed to authenticate with Tableau Server")

def sign_out_tableau() -> bool:
    """
    Sign out from Tableau Server and clear session token
    """
    global TABLEAU_SESSION_TOKEN
    
    if not TABLEAU_SESSION_TOKEN:
        print("ℹ️ No active session to sign out from")
        return True
        
    print("🚪 Signing out from Tableau Server...")
    
    url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_API_VERSION}/auth/signout"
    headers = {
        "X-Tableau-Auth": TABLEAU_SESSION_TOKEN,
        "Accept": "application/xml"
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=TABLEAU_TIMEOUT)
        
        if response.status_code in [200, 204]:  # 204 is also success for sign-out
            print("✅ Successfully signed out")
            TABLEAU_SESSION_TOKEN = None
            return True
        else:
            print(f"⚠️ Sign out returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Sign out failed: {e}")
        return False
