import os
import pandas as pd
from azure_utils.keyvault import get_secret_value_from_keyvault
from azure_utils.blob import setup_blob_service_client, setup_blob_container_client, get_blob_metadata, upload_bytes_blob, download_blob

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_BLOB_CONNECTION_STRING_SECRET_NAME = os.getenv("AZ_BLOB_CONNECTION_STRING_SECRET_NAME")
AZ_BLOB_CONNECTION_STRING_SECRET_VALUE = get_secret_value_from_keyvault(AZ_KEYVAULT_URL, AZ_BLOB_CONNECTION_STRING_SECRET_NAME)
blob_service_client = setup_blob_service_client(AZ_BLOB_CONNECTION_STRING_SECRET_VALUE)


class FileUploadManager:
    def __init__(self):
        self.blob_service_client = blob_service_client

    def get_blob_metadata(self, container_name):
        blob_container_client = setup_blob_container_client(self.blob_service_client, container_name)
        return get_blob_metadata(blob_container_client)
        
    def upload_file(self, container_name, file_bytes, file_name):
        blob_container_client = setup_blob_container_client(self.blob_service_client, container_name)
        return upload_bytes_blob(blob_container_client, file_bytes, file_name)
    
    def download_file(self, container_name, file_name):
        blob_container_client = setup_blob_container_client(self.blob_service_client, container_name)
        return download_blob(blob_container_client, file_name)
