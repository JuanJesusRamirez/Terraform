import os
from openai import AzureOpenAI
from typing import Any

def setup_openai_client(az_openai_endpoint: str, az_openai_key: str) -> AzureOpenAI:
    """
    Initializes the Azure OpenAI client and returns the client instance.

    Args:
        az_openai_endpoint (str): The endpoint URL for Azure OpenAI.
        az_openai_key (str): The API key for Azure OpenAI.

    Returns:
        AzureOpenAI: The Azure OpenAI client.
    """
    try:
        client = AzureOpenAI(
            api_key=az_openai_key,
            api_version="2024-05-01-preview",
            azure_endpoint=az_openai_endpoint
        )
        print("OpenAI client setup successfully.")
        return client
    except Exception as e:
        print(f"Error setting up OpenAI client: {e}")
        return None