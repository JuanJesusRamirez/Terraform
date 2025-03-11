import os

# Import necessary modules for blob synchronization
from azure_utils.keyvault import get_secret_value_from_keyvault
from azure_utils.blob import setup_blob_service_client
from app.file_upload.services.blob_sync_service import BlobSyncService


async def startup_event():
    """
    Startup event handler that runs when the application starts.
    Synchronizes the local directory with blob storage.
    """
    try:
        print("Starting blob synchronization...")
        
        # Get environment variables
        az_keyvault_url = os.getenv('AZ_KEYVAULT_URL')
        az_blob_connection_string_secret_name = os.getenv('AZ_BLOB_CONNECTION_STRING_SECRET_NAME')
        
        # Get blob storage connection string from Key Vault
        az_blob_connection_string = get_secret_value_from_keyvault(
            az_keyvault_url, 
            az_blob_connection_string_secret_name
        )
        
        # Set up blob service client
        blob_service_client = setup_blob_service_client(az_blob_connection_string)
        
        # Define the local directory path
        if os.path.exists(os.path.join("app")):
            local_directory = os.path.join("app", "agents", "sources", "outlook-2025")
        else:
            local_directory = os.path.join("backend", "app", "agents", "sources", "outlook-2025")
        
        # Create the local directory if it doesn't exist
        os.makedirs(local_directory, exist_ok=True)
        
        # Initialize and run the sync service
        sync_service = BlobSyncService(blob_service_client)
        downloaded_files = sync_service.sync_container_to_local("outlook-2025", local_directory)
        
        print(f"Blob synchronization completed. Downloaded {len(downloaded_files)} files.")
    except Exception as e:
        print(f"Error during blob synchronization: {str(e)}")


