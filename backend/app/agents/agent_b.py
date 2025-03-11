#1. Import Libraries

# Standard libraries
import os
from dotenv import load_dotenv
from typing import TypedDict
import json
import pandas as pd

# Third-party libraries
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Custom modules
from azure_utils.keyvault import get_secret_value_from_keyvault
from azure_utils.openai import setup_openai_client
from azure_utils.blob import get_blob_metadata, setup_blob_container_client, setup_blob_service_client


#2. Get Credentials

# Load environment variables
load_dotenv()

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_OPENAI_KEY_SECRET_NAME = os.getenv('AZ_OPENAI_KEY_SECRET_NAME')
AZ_OPENAI_ENDPOINT = os.getenv('AZ_OPENAI_ENDPOINT')
AZ_BLOB_CONNECTION_STRING_SECRET_NAME = os.getenv('AZ_BLOB_CONNECTION_STRING_SECRET_NAME')
AZ_BLOB_CONNECTION_STRING = get_secret_value_from_keyvault(AZ_KEYVAULT_URL, AZ_BLOB_CONNECTION_STRING_SECRET_NAME)
AZ_OPENAI_KEY = get_secret_value_from_keyvault(AZ_KEYVAULT_URL,AZ_OPENAI_KEY_SECRET_NAME)


blob_service_client = setup_blob_service_client(AZ_BLOB_CONNECTION_STRING )


#3. Define Agent Tools
# Agent Tools
@tool
def get_blob_container_metadata() -> dict:
    """
    Retrieves metadata about the file blob container file.

    The metadata includes information about container, such as their 
    descriptions, and the corresponding Blob Storage container 
    names where the documents are stored.

    Returns:
        dict: A dictionary containing the metadata of the blob container file, 
              including each description, and Blob Storage container name.
    """
    if os.path.exists(os.path.join("app")):
        json_path = os.path.join("app", "agents", "all_vector_dbs.json")
        with open(json_path, 'r') as file:
            # Convertir el JSON a un diccionario
            metadata_vectordb = json.load(file)
    else:
        with open('all_vector_dbs.json', 'r') as file:
            # Convertir el JSON a un diccionario
            metadata_vectordb = json.load(file)
    
    return metadata_vectordb

@tool
def get_blob_files_metadata(container_name: str) -> pd.DataFrame:
    """
    Retrieves metadata of all files in an Azure Blob Storage container, which are the same files indexed in 
    the OpenAI vector store, and returns it as a DataFrame.

    Args:
        container_name (str): The name of the container in Azure Blob Storage from which to retrieve metadata.

    Returns:
        pd.DataFrame: A DataFrame containing metadata for the blobs (files) within the specified container. 
                      The DataFrame may include columns such as file names, size, last modified date, and other information.
    """
    container_blob_client = setup_blob_container_client(blob_service_client, container_name)
    metadata_df = get_blob_metadata(container_blob_client)['Name']
    
    return metadata_df

@tool
def search_information_on_single_file(user_input: str, file_name:str) -> str:
    """
    Retrieve information from a specific file based on user input.

    This function processes a user-provided query to extract and return relevant insights 
    from a single PDF document identified by its file name or path. 

    Args:
        user_input (str): The user-provided query or search term for retrieving data from file.
        file_name (str): The name or path of the PDF file to be queried for the information.
                         
    Returns:
        str: A formatted string containing the extracted insights. If an error occurs during processing, a descriptive 
             error message is returned.
    """

    openai_client = setup_openai_client(AZ_OPENAI_ENDPOINT,AZ_OPENAI_KEY)
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

    if os.path.exists(os.path.join("app")):
        relative_path = os.path.join("app", "agents", "sources", "outlook-2025", file_name)
    else:
        relative_path = os.path.join("sources", "outlook-2025", file_name)

    # Convertir a ruta absoluta
    file_path = os.path.abspath(relative_path)
    

    if os.path.exists(file_path):
        print(f"El archivo existe en la ruta: {file_path}.")
        # Leer el archivo
        with open(file_path, 'rb') as file:
            content = file.read()
            print("El archivo ha sido leído correctamente.")
    else:
        print(f"El archivo no existe en la ruta: {file_path}.")
        return f"El archivo no existe en la ruta: {file_path}"

    message_file = openai_client.files.create(
    file=open(file_path, "rb"), purpose="assistants"
    )
    # Create a thread and attach the file to the message
    thread = openai_client.beta.threads.create(
    messages=[
        {
        "role": "user",
        "content": user_input,
        # Attach the new file to the message.
        "attachments": [
            { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
        ],
        }
    ]
    )

    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=user_input)
    messages = list(openai_client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    
    annotations = message_content.annotations
  
    citations = []
    for index, annotation in enumerate(annotations):
        fragment = annotation.text
        citation_text = f"[{index}]"
        message_content.value = message_content.value.replace(fragment, citation_text)
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = openai_client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}\n")
                   
    combine_message = message_content.value+"\n\n"+"\n".join(citations)
    

    return combine_message 

#5. Define Nodes and Other Functions
def assistant(state: MessagesState):
    """
    Assistant function to generate a response based on the current state of messages.

    This function creates a system message with specific instructions for the assistant to follow.
    It then invokes the language model with the system message and the current state of messages,
    and returns the generated response.

    Args:
        state (MessagesState): The current state of the messages.

    Returns:
        dict: A dictionary containing the generated messages.
    """
    
    sys_msg = SystemMessage(content='''
            - You are an expert financial market analyst. Your primary role is to examine and evaluate 
            the potential future prospects of global financial markets.

            - Consider and analyze factors such as:
                - Economic indicators
                - Geopolitical events
                - Technological advancements

            - Use recent news or headlines from reputable sources to provide an impartial 
            evaluation of expected trends and challenges.

            - Follow these functional guidelines:
                
                1. get_blob_container_metadata():
                - Execute this function first to retrieve metadata at the container level.

                2. get_blob_files_metadata():
                - Use this function only after completing the metadata retrieval at the container level.

                3. search_information_on_single_file():
                - This is the primary tool for extracting insights.
                - Mandatory to execute after completing the first two steps.
                
            - When querying:
                - Handle single files individually.
                - Apply the same query across multiple files if needed to associate and synthesize relevant information.

            - If any detail is unclear or unavailable:
                - Ask the user for clarification once before proceeding.
                - Avoid making assumptions.

            - Deliver analyses that are:
                - Precise
                - Actionable
                - Directly tailored to the user’s request
                - Use comparative tables to present data and insights clearly and concisely.
            '''
            )
    
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


os.environ["AZURE_OPENAI_API_KEY"] = get_secret_value_from_keyvault(AZ_KEYVAULT_URL,"AzureOpenAIKeyRalfR3V2")
os.environ["AZURE_OPENAI_ENDPOINT"] =  os.getenv('AZ_OPENAI_ENDPOINT_V2') 

#6. Include LLM and Tools in Agent
llm = AzureChatOpenAI(
    azure_deployment="o3-mini", 
    api_version="2024-12-01-preview", 
    reasoning_effort = "low"
)

tools = [get_blob_container_metadata, get_blob_files_metadata, search_information_on_single_file]

llm_with_tools = llm.bind_tools(tools)

#7. Define Agent using Langraph and Langchain

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)  # Add the assistant node
builder.add_node("tools", ToolNode(tools))  # Add the tools node

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")  # Start with the assistant node
builder.add_conditional_edges("assistant", tools_condition)  # Conditionally move to tools based on tools_condition

# Conditionally move to END or back to assistant based on supervisor's evaluation
builder.add_edge("tools", "assistant")

# Set up memory saver for the graph
memory = MemorySaver()

# Compile the graph with the memory saver as the checkpointer
graph = builder.compile(checkpointer=memory)

