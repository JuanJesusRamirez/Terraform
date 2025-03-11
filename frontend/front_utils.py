import streamlit as st
import requests
import os
import time

import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import io
from io import BytesIO

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

API_URL = os.environ.get("BACKEND_API_URL")

def wait_for_backend(message="Waiting for backend to start...", retry_interval=2, max_retries=30):
    """
    Display a waiting message while attempting to connect to the backend.
    
    Args:
        message (str): The message to display.
        retry_interval (int): Number of seconds to wait between retries.
        max_retries (int): Maximum number of retries before giving up.
        
    Returns:
        bool: True if the backend is available, False if max retries were exceeded.
    """
    api_url = os.environ.get("BACKEND_API_URL")
    
    with st.spinner(message):
        for _ in range(max_retries):
            try:
                # Try to connect to any endpoint
                response = requests.get(f"{api_url}/api/ms_auth/get_auth_url", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(retry_interval)
    
    return False

class BaseAPIClient:
    """Base class to handle connection with the FastAPI with retry mechanism."""
    def __init__(self, api_url=None):
        self.api_url = api_url or os.environ.get("BACKEND_API_URL")

    def _request(self, method, endpoint, **kwargs):
        """Helper method to send requests to the API with retry logic."""
        try:
            response = method(f"{self.api_url}{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Check if it's a connection error (backend not started yet)
            if isinstance(e, (requests.ConnectionError, requests.Timeout)):
                if wait_for_backend():
                    # Try again after backend is available
                    try:
                        response = method(f"{self.api_url}{endpoint}", **kwargs)
                        response.raise_for_status()
                        return response.json()
                    except:
                        return {"error": "Error processing request after backend started"}
                else:
                    return {"error": "Backend service is not available. Please try again later."}
            return {"error": f"Could not connect to the server: {e}"}

    def _get(self, endpoint):
        """Helper method to send GET requests to the API."""
        return self._request(requests.get, endpoint)

    def _post(self, endpoint, json=None):
        """Helper method to send POST requests to the API."""
        return self._request(requests.post, endpoint, json=json)
    
def log_function():
    logout_url = requests.get(f"{API_URL}/api/ms_auth/get_logout_url").json()
    aida_url = requests.get(f"{API_URL}/api/ms_auth/get_aida_url").json()

    st.markdown(f'''
        <div style="text-align: center;">
            <div style="display: inline-block; width: 48%; text-align: center;">
                <a href="{logout_url}" target="_self" style="text-decoration:none;">
                    <button style="padding:5px 10px; font-size:15px; width:100%; 
                            background-color: #f44336; color: white; 
                            border: none; border-radius: 4px;">
                        🔒 Logout
                    </button>
                </a>
         
        </div>
    ''', unsafe_allow_html=True)
    


def detect_scanned_pdf(pdf_bytes: bytes) -> bool:
    """
    Checks if the total number of characters in a PDF file provided as bytes is 1000 or more.
    Returns True if the PDF is likely to be scanned or needs OCR based on the character count.

    Args:
        pdf_bytes (bytes): PDF file in bytes format.

    Returns:
        bool: True if the total number of characters is 1000 or more, indicating the need for OCR,
              False otherwise.
    """
    total_characters: int = 0  # Initialize total_characters counter

    try:
        # Create a BytesIO object to handle the byte input
        pdf_stream = BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)  # Create a PDF reader object

        # Iterate through each page in the PDF
        for page in pdf_reader.pages:
            # Extract text from the page and count characters
            text = page.extract_text()
            if text:  # Check if text extraction was successful
                total_characters += len(text)

            # Return True if the total characters exceed 1000
            if total_characters >= 10:
                return True

        # Return False if the total characters are less than 1000
        return False
    
    except Exception as e:
        # Print the error message and return False if an error occurs
        print(f"Error processing PDF: {e}")
        return False
 
   