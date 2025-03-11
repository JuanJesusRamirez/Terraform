from azure_utils.keyvault import get_secret_value_from_keyvault
from azure_utils.openai import setup_openai_client
from dotenv import load_dotenv
import os

load_dotenv()

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_OPENAI_KEY_SECRET_NAME = os.getenv('AZ_OPENAI_KEY_SECRET_NAME')
AZ_OPENAI_ENDPOINT = os.getenv('AZ_OPENAI_ENDPOINT')
AZ_OPENAI_KEY = get_secret_value_from_keyvault(AZ_KEYVAULT_URL,AZ_OPENAI_KEY_SECRET_NAME)


from openai import AzureOpenAI

openai_client = AzureOpenAI(
        api_key=AZ_OPENAI_KEY ,
        api_version="2024-05-01-preview",
        azure_endpoint=AZ_OPENAI_ENDPOINT
    )


assistant = openai_client.beta.assistants.create(
    name="Search Assistant (gpt-4o-mini)",
    instructions=(
        "You suggest better questions based on the initial prompt, just qhen you can not retrieve information"
        "You search for information in the documents you are asked to "
        "Your responses should be limited to the content of the requested document(s), ensuring accuracy and relevance. "
        "Do not provide any extra context, information, or references from other documents unless explicitly asked for."
    ),
    model="gpt-4o-mini",
    tools=[{"type": "file_search"}]
)

file_name = "Amundi - Investment Outlook 2025.pdf"
relative_path = os.path.join("backend","app", "agents", "sources", "outlook-2025", file_name)
    
# Convertir a ruta absoluta
file_path = os.path.abspath(relative_path)
    
# Upload the user provided file to OpenAI
message_file = openai_client.files.create(
  file=open(file_path, "rb"), purpose="assistants"
)
 
# Create a thread and attach the file to the message
thread = openai_client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "How many company shares were outstanding last quarter?",
      # Attach the new file to the message.
      "attachments": [
        { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
      ],
    }
  ]
)
 
# The thread now has a vector store with that file in its tool resources.
print(thread.tool_resources.file_search)
run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Hi")

# Check the run status to ensure it completed successfully
print(f"Run status: {run.status}")
if run.status == "completed":
    # Retrieve messages without the run_id parameter
    messages = list(openai_client.beta.threads.messages.list(thread_id=thread.id))
    
    if messages:
        print(f"Number of messages: {len(messages)}")
        # Print each message with its role and content
        for msg in messages:
            print(f"Role: {msg.role}")
            # Extract and print the text content
            for content_item in msg.content:
                if content_item.type == "text":
                    print(f"Content: {content_item.text.value}")
    else:
        print("No messages were returned.")
else:
    print(f"Run did not complete successfully. Status: {run.status}")
    if hasattr(run, 'last_error'):
        print(f"Error: {run.last_error}")






