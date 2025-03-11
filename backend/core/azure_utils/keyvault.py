import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_value_from_keyvault(keyvault_url: str, secret_name: str) -> str:
  """
  Retrieves a connection string from Azure Key Vault.

  Args:
      secret_name (str): The name of the secret containing the connection string.
      key_vault_url (str): The URL of the Azure Key Vault.

  Returns:
      str: The connection string retrieved from Key Vault, or None on error.
  """
  try:
    # Load environment variables (optional, for local development)
    load_dotenv()

    # Create an Azure credential object
    credential = DefaultAzureCredential()

    # Create a SecretClient to access Key Vault
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

    # Get the secret containing the connection string
    connection_string = secret_client.get_secret(secret_name).value

    # Print success message
    print(f"Successfully retrieved connection string for '{secret_name}' from Key Vault '{keyvault_url}'.")
    return connection_string

  except Exception as e:
    # Print error message
    print(f"Failed to retrieve connection string for '{secret_name}' from Key Vault '{keyvault_url}': {e}")
    return None