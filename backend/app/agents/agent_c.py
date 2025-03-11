#1. Import Libraries

# Standard libraries
import os
from dotenv import load_dotenv
from azure_utils.keyvault import get_secret_value_from_keyvault

#2. Get Credentials

# Load environment variables
load_dotenv()

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_OPENAI_KEY_SECRET_NAME = os.getenv('AZ_OPENAI_KEY_SECRET_NAME')
AZ_OPENAI_ENDPOINT = os.getenv('AZ_OPENAI_ENDPOINT_V2')
AZ_OPENAI_KEY = get_secret_value_from_keyvault(AZ_KEYVAULT_URL,"AzureOpenAIKeyRalfR3V2")


os.environ["AZURE_OPENAI_API_KEY"] = AZ_OPENAI_KEY 
os.environ["AZURE_OPENAI_ENDPOINT"] = AZ_OPENAI_ENDPOINT

from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="o3-mini", 
    api_version="2024-12-01-preview", 
    reasoning_effort = "low"
)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg
print(ai_msg.content)

