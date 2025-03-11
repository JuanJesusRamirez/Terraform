import os
import streamlit as st
import pandas as pd
import json
import base64
from io import BytesIO
from datetime import datetime, timedelta
import time
import requests

from front_utils import log_function, detect_scanned_pdf, BaseAPIClient, wait_for_backend


API_URL = os.environ.get("BACKEND_API_URL")

class APIClient(BaseAPIClient):
    """Base class to handle connection with the FastAPI with retry mechanism."""
    pass

class FileUploadClient(APIClient):
    """Handles connection with the FastAPI for user requests."""
    def upload_file(self, container_name, file_bytes, file_name):
        files = {"file": (file_name, file_bytes)}
        try:
            response = requests.post(f"{self.api_url}/api/file_upload/upload_file/{container_name}", files=files)
            response.raise_for_status()
            return response
        except requests.RequestException:
            # Try waiting for the backend
            if wait_for_backend("Waiting for backend file service..."):
                try:
                    response = requests.post(f"{self.api_url}/api/file_upload/upload_file/{container_name}", files=files)
                    response.raise_for_status()
                    return response
                except:
                    st.error("Error uploading file after backend started")
                    return None
            st.error("Backend service is not available. Please try again later.")
            return None

    def get_blob_metadata(self, container_name):
        try:
            response = requests.get(f"{self.api_url}/api/file_upload/get_blob_metadata/{container_name}").json()
            if "error" in response:
                return pd.DataFrame()  # Returns an empty DataFrame in case of error
            return pd.DataFrame(response)
        except requests.RequestException:
            # Try waiting for backend
            if wait_for_backend("Loading file metadata..."):
                try:
                    response = requests.get(f"{self.api_url}/api/file_upload/get_blob_metadata/{container_name}").json()
                    if "error" in response:
                        return pd.DataFrame()
                    return pd.DataFrame(response)
                except:
                    return pd.DataFrame()
            return pd.DataFrame()

    def download_blob(self, container_name, file_name):
        try:
            return requests.get(f"{self.api_url}/api/file_upload/download_blob/{container_name}/{file_name}")
        except requests.RequestException:
            if wait_for_backend("Connecting to file service..."):
                try:
                    return requests.get(f"{self.api_url}/api/file_upload/download_blob/{container_name}/{file_name}")
                except:
                    st.error("Error downloading file after backend started")
                    return None
            st.error("Backend service is not available. Please try again later.")
            return None

class FileProcessor:
    """Handles file processing logic."""
    def __init__(self, upload_client):
        self.upload_client = upload_client

    def process_file(self, container_name, file_bytes, file_name, file_type):
        if file_type == 'pdf':
            if detect_scanned_pdf(file_bytes):
                self.upload_client.upload_file(container_name, file_bytes, file_name)
                st.success(f"The file '{file_name}' has been successfully uploaded to Azure Blob Storage.")
                return True
            else:
                st.error(f"The file '{file_name}' was not uploaded. It is likely scanned. Please process it with OCR and try again.")
                return False

class UIHandler:
    """Handles the UI logic."""
    def __init__(self, upload_client, file_processor):
        self.upload_client = upload_client
        self.file_processor = file_processor

    def init_state_variables(self):
        defaults = {"file_bytes": None, "pdf_base64": None}
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def load_page(self):
        self.init_state_variables()
        st.markdown("##### Upload and Download Files")
        col1, col2, col3 = st.columns([6, 1, 8])
        with col1:
            self.upload_section()
        with col3:
            self.download_section()
            
        with st.sidebar:
            st.markdown("---")
            log_function()
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.write(""" -- 1.5.0 --""")

    def upload_section(self):
        st.write("*Want to add more files? Do it here:*")
        st.write("**:large_blue_circle: File Upload**")
        container_name_dict = { 
                                "Outlook 2025": "outlook-2025"
                               }
        selected_container = st.selectbox("Data Source:", list(container_name_dict.keys()))
        st.session_state.ablob_selected_container_name = container_name_dict[selected_container]
        
        st.session_state.uploaded_files = st.file_uploader("Choose files (PDF)", type=["pdf"], accept_multiple_files=True)
        if st.button(f'Upload to ({st.session_state.ablob_selected_container_name})'):
            self.handle_file_upload()

    def handle_file_upload(self):
        if st.session_state.uploaded_files:
            files_uploaded = 0
            files_skipped = 0
            for uploaded_file in st.session_state.uploaded_files:
                file_bytes = uploaded_file.read()
                file_name = uploaded_file.name
                if not st.session_state.metadata_df.empty and file_name in st.session_state.metadata_df['Name'].tolist():
                    st.warning(f"The file '{file_name}' already exists and will be skipped.")
                    files_skipped += 1
                else:
                    file_type = uploaded_file.type.split('/')[-1]
                    if self.file_processor.process_file(st.session_state.ablob_selected_container_name, file_bytes, file_name, file_type):
                        files_uploaded += 1
            if files_uploaded > 0:
                st.success(f"{files_uploaded} files were successfully uploaded.")
            if files_skipped > 0:
                st.info(f"{files_skipped} files were skipped because they already existed.")

    def download_section(self):
        st.write("*Explore the files I use to answer you here:*")
        st.write("**:large_blue_square: File Download**")
        st.session_state.metadata_df = self.upload_client.get_blob_metadata(st.session_state.ablob_selected_container_name)
        if not st.session_state.metadata_df.empty:
            st.session_state.selected_file = st.selectbox("Search file: ", st.session_state.metadata_df['Name'])
            if st.button('Select'):
                self.handle_file_download()

    def handle_file_download(self):
        response = self.upload_client.download_blob(st.session_state.ablob_selected_container_name,st.session_state.selected_file)
        if response.status_code == 200:
            st.session_state.file_bytes = response.content
            file_type = st.session_state.selected_file.split('.')[-1]
            if file_type == 'pdf':
                st.download_button(
                    label="Download",
                    data=st.session_state.file_bytes,
                    file_name=st.session_state.selected_file,
                    mime="application/pdf"
                )
        else:
            st.error("Failed to download the file.")

def run():
    upload_client = FileUploadClient()
    file_processor = FileProcessor(upload_client)
    ui_handler = UIHandler(upload_client, file_processor)
    ui_handler.load_page()
