import os
import pandas as pd
from typing import List
from azure_utils.blob import setup_blob_service_client, setup_blob_container_client, get_blob_metadata, download_blob

class BlobSyncService:
    """
    Service for synchronizing files between Azure Blob Storage and local directories.
    This service ensures that files in the local directory match those in blob storage.
    """
    
    def __init__(self, blob_service_client, local_directory: str = None):
        """
        Initialize the BlobSyncService with a blob service client and local directory.
        
        Args:
            blob_service_client: Azure blob service client
            local_directory (str, optional): Path to the local directory to synchronize
        """
        self.blob_service_client = blob_service_client
        self.local_directory = local_directory
    
    def sync_container_to_local(self, container_name: str, local_directory: str = None) -> List[str]:
        """
        Synchronizes files from an Azure Blob container to a local directory.
        Downloads files that exist in the container but are not in the local directory.
        
        Args:
            container_name (str): Name of the Azure blob container
            local_directory (str, optional): Path to the local directory. If None, uses the instance's local_directory
            
        Returns:
            List[str]: List of files that were downloaded
        """
        if local_directory is None:
            local_directory = self.local_directory
            
        if local_directory is None:
            raise ValueError("Local directory not specified")
        
        # Create the local directory if it doesn't exist
        os.makedirs(local_directory, exist_ok=True)
        
        # Get the container client
        container_client = setup_blob_container_client(self.blob_service_client, container_name)
        
        # Get list of files in blob storage
        blob_metadata_df = get_blob_metadata(container_client)
        blob_files = blob_metadata_df['Name'].tolist()
        
        # Get list of files in local directory
        local_files = os.listdir(local_directory) if os.path.exists(local_directory) else []
        
        # Find files that are in blob storage but not locally
        missing_files = list(set(blob_files) - set(local_files))
        
        downloaded_files = []
        for file_name in missing_files:
            try:
                # Download the file
                file_bytes = download_blob(container_client, file_name)
                
                # Save the file locally
                file_path = os.path.join(local_directory, file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_bytes)
                
                downloaded_files.append(file_name)
                print(f"Downloaded: {file_name}")
            except Exception as e:
                print(f"Error downloading {file_name}: {str(e)}")
        
        print(f"Synchronized {len(downloaded_files)} files from '{container_name}' to '{local_directory}'")
        return downloaded_files
