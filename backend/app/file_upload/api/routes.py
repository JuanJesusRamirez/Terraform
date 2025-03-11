from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse
from app.file_upload.services.file_upload_handler import FileUploadManager
from pydantic import BaseModel
from typing import List, Dict
from typing import Any
from io import BytesIO
import os
import asyncio

# Import the sync service
from app.file_upload.services.blob_sync_service import BlobSyncService
from azure_utils.blob import setup_blob_service_client
from azure_utils.keyvault import get_secret_value_from_keyvault

file_upload_manager= FileUploadManager()
router = APIRouter()

@router.get("/file_upload/get_blob_metadata/{container_name}")
def get_blob_metadata(container_name: str):
    return file_upload_manager.get_blob_metadata(container_name)

@router.post("/file_upload/upload_file/{container_name}")
async def upload_file(container_name: str, file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()  # Leer los bytes del archivo
        result = file_upload_manager.upload_file(container_name, file_bytes, file.filename)
        
        # If the container is outlook-2025, sync the file to the local directory
        if container_name == "outlook-2025":
            # Schedule the sync operation to run in the background
            asyncio.create_task(sync_new_file(container_name, file.filename, file_bytes))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al subir el archivo: {str(e)}")
    
@router.get("/file_upload/download_blob/{container_name}/{file_name}")
def download_blob(container_name:str, file_name: str):
    file_bytes = file_upload_manager.download_file(container_name,file_name)  # Debe devolver bytes

    if not file_bytes:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        BytesIO(file_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'}
    )

async def sync_new_file(container_name: str, file_name: str, file_bytes: bytes):
    """
    Synchronize a newly uploaded file to the local directory.
    
    Args:
        container_name (str): Name of the blob container
        file_name (str): Name of the file
        file_bytes (bytes): The file content in bytes
    """
    try:
        # Determine the local directory path
        if os.path.exists(os.path.join("app")):
            local_directory = os.path.join("app", "agents", "sources", container_name)
        else:
            local_directory = os.path.join("backend", "app", "agents", "sources", container_name)
        
        # Create the local directory if it doesn't exist
        os.makedirs(local_directory, exist_ok=True)
        
        # Save the file locally
        file_path = os.path.join(local_directory, file_name)
        with open(file_path, 'wb') as file:
            file.write(file_bytes)
        
        print(f"Synchronized new file: {file_name} to {local_directory}")
    except Exception as e:
        print(f"Error synchronizing new file {file_name}: {str(e)}")
