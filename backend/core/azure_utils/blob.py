from azure.storage.blob import BlobServiceClient, ContainerClient
from io import BytesIO
import pandas as pd

def setup_blob_service_client(connection_string: str) -> BlobServiceClient:
    """
    Sets up and returns a BlobServiceClient instance.

    Args:
        connection_string (str): The connection string to access Azure Blob Storage.

    Returns:
        BlobServiceClient: The client instance to interact with Azure Blob Storage.
    """
    try:
        # Connect to the Blob Storage service
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("Blob service client successfully set up.")
        return blob_service_client
    except Exception as e:
        print(f"Error setting up Blob service client: {str(e)}")
        raise

def setup_blob_container_client(blob_service_client: BlobServiceClient, container_name: str) -> ContainerClient:
    """
    Sets up and returns a ContainerClient instance for a specific container.

    Args:
        blob_service_client (BlobServiceClient): The BlobServiceClient instance to access Azure Blob Storage.
        container_name (str): The name of the container in Azure Blob Storage.

    Returns:
        ContainerClient: The client instance to interact with a specific container in Azure Blob Storage.
    """
    try:
        # Get the client for the specific container
        container_client = blob_service_client.get_container_client(container_name)
        print(f"Container client for '{container_name}' successfully set up.")
        return container_client
    except Exception as e:
        print(f"Error setting up container client: {str(e)}")
        raise
    
def upload_bytes_blob(container_client: ContainerClient, bytes_file: bytes, filename: str) -> None:
    """
    Uploads a file to Azure Blob Storage using an existing container client.

    Args:
        container_client (ContainerClient): The ContainerClient instance for Azure Blob Storage.
        bytes_file (bytes): The file content as bytes to upload.
        filename (str): The name of the file in Azure Blob Storage.

    Returns:
        None
    """
    try:
        # Upload the file to the container
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(bytes_file, overwrite=True)

        print(f"File '{filename}' successfully uploaded to Azure Blob Storage.")
    except Exception as e:
        print(f"Error uploading file to Azure Blob Storage: {str(e)}")
        raise

def get_blob_metadata(container_client: ContainerClient) -> pd.DataFrame:
    """
    Retrieves metadata (name, last modified time, URL) for blobs in a given Azure Blob Storage container.

    Args:
        connection_string (str): Connection string for Azure Blob Storage.
        container_name (str): Name of the container to retrieve blob metadata from.

    Returns:
        pd.DataFrame: DataFrame containing blob metadata (name, last modified, URL).
    """

    try:
        # Initialize list to store blob metadata
        blob_metadata = []

        # List blobs in the container
        blobs = container_client.list_blobs()

        # Iterate over blobs and retrieve metadata
        for blob in blobs:
            blob_name = blob.name
            last_modified = blob.last_modified
            blob_url = f"{container_client.url}/{blob_name}"  # Assuming public access enabled

            # Append blob metadata to list
            blob_metadata.append({
                'Name': blob_name,
                'Last Modified': last_modified,
                'URL': blob_url
            })

        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(blob_metadata)
        return df

    except Exception as e:
        print(f"Failed to retrieve blob metadata from container '{container_name}': {e}")
        return pd.DataFrame()
    
def download_blob(container_client: ContainerClient, filename: str) -> bytes:
    """
    Downloads a file from Azure Blob Storage and returns its content in bytes format.

    Args:
        container_client (ContainerClient): The client for the container in Azure Blob Storage.
        filename (str): The name of the file to download.

    Returns:
        bytes: The content of the file in bytes format.
    """
    try:
        # Get the blob client
        blob_client = container_client.get_blob_client(filename)
        
        # Download the blob content
        blob_data = blob_client.download_blob()
        blob_bytes = blob_data.readall()
        
        print(f"File '{filename}' downloaded successfully.")
        return blob_bytes
    except Exception as e:
        print(f"Error downloading file '{filename}': {str(e)}")
        raise