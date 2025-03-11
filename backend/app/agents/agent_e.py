
import os  
import base64
from openai import AzureOpenAI  
from azure_utils.keyvault import get_secret_value_from_keyvault

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_OPENAI_KEY_SECRET_NAME = os.getenv('AZ_OPENAI_KEY_SECRET_NAME')
AZ_OPENAI_ENDPOINT = os.getenv('AZ_OPENAI_ENDPOINT_V2')
AZ_OPENAI_KEY = get_secret_value_from_keyvault(AZ_KEYVAULT_URL,"AzureOpenAIKeyRalfR3V2")

# Inicialización del cliente del Azure OpenAI Service con autenticación basada en claves    
client = AzureOpenAI(  
    azure_endpoint=AZ_OPENAI_ENDPOINT,  
    api_key=AZ_OPENAI_KEY,  
    api_version="2024-12-01-preview",
)
deployment = "o3-mini"
    
    
# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

#Prepare la indicación de chat 
chat_prompt = [
    {
        "role": "developer",
        "content": [
            {
                "type": "text",
                "text": "Es un asistente de inteligencia artificial que ayuda a los usuarios a encontrar información."
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "hola"
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "¡Hola! ¿En qué puedo ayudarte hoy?"
            }
        ]
    }
] 
    
# Incluir el resultado de voz si la voz está habilitada  
messages = chat_prompt  
    
# Generar finalización  
completion = client.chat.completions.create(  
    model=deployment,
    messages=messages,
    max_completion_tokens=100000,
    stop=None,  
    stream=False
)

print(completion.to_json())  
    