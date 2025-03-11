from setuptools import setup, find_packages

setup(
    name="azure_utils",
    version="0.1",
    packages=find_packages(),
    description="Utility functions for Azure services",
    python_requires=">=3.11.9",
    install_requires=[
        "azure-keyvault-secrets==4.7.0", # For Azure Key Vault (Secret Management) - Library to access and manage secrets in Azure Key Vault
        "python-dotenv==1.0.0", # For Python-dotenv - Reads the key-value pair from .env file and adds them to environment variable
        "azure-identity==1.15.0", # For Azure Identity - Provides a set of credential classes for authenticating to Azure services,
        "openai==1.58.1", # For OpenAI - Python client library for OpenAI API
        "azure-storage-blob==12.20.0", # For Azure Storage Blob - Library to interact with Azure Blob Storage
        "pandas==2.2.2", # For Pandas - Library to work with data in Python
        "azure-cosmos==4.7.0", # For Azure Cosmos - Library to interact with Azure Cosmos DB
    ]
)