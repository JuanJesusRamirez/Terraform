from azure.cosmos import CosmosClient
from datetime import datetime
import pandas as pd

def setup_cosmos_client(account_url: str, account_key: str, database_name: str, container_name: str) -> CosmosClient:
    """
    Initializes the Cosmos DB client and returns a container client.

    Args:
        account_url (str): The URL of the Cosmos DB account.
        account_key (str): The key for the Cosmos DB account.
        database_name (str): The name of the Cosmos DB database.
        container_name (str): The name of the Cosmos DB container.

    Returns:
        CosmosClient: The container client.
    """
    try:
        # Initialize Cosmos DB client
        client = CosmosClient(account_url, credential=account_key)
        # Access the database
        database = client.get_database_client(database_name)
        # Access the container
        container_client = database.get_container_client(container_name)
        return container_client
    except Exception as e:
        print(f"Error initializing Cosmos DB client: {e}")
        return None

def save_conversation(container_client: CosmosClient, user_id: str, conversation_id: str, conversation_name: str, conversation_data: dict) -> None:
    """
    Saves or updates a conversation document in Cosmos DB.

    Args:
        container_client (CosmosClient): The Cosmos DB container client.
        user_id (str): The ID of the user.
        conversation_id (str): The ID of the conversation.
        conversation_name (str): The name of the conversation.
        conversation_data (dict): The content of the conversation.

    Returns:
        None
    """
    try:
        # Get the current UTC time
        last_modified = datetime.utcnow().isoformat()

        # Create the document structure
        conversation_document = {
            'id': conversation_id,
            'user_id': user_id,
            'conversation_name': conversation_name,
            'conversation_content': conversation_data,
            'last_modified': last_modified
        }

        # Upsert the document in Cosmos DB
        container_client.upsert_item(conversation_document)
        print(f"Successfully saved/updated conversation '{conversation_id}' for user '{user_id}'.")
    except Exception as e:
        print(f"Error saving/updating conversation '{conversation_id}' for user '{user_id}': {e}")

def read_conversation(container_client: CosmosClient, conversation_id: str) -> dict:
    """
    Retrieves a conversation document by its ID.

    Args:
        container_client (CosmosClient): The Cosmos DB container client.
        conversation_id (str): The ID of the conversation.

    Returns:
        dict: The content of the conversation, or None if not found.
    """
    try:
        # Query to get the conversation by ID
        query = "SELECT * FROM c WHERE c.id=@conversation_id"
        parameters = [{"name": "@conversation_id", "value": conversation_id}]

        # Execute the query
        items = list(container_client.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        # Return the conversation content if exists
        if items:
            return items[0].get('conversation_content', {})
        return None
    except Exception as e:
        print(f"Error reading conversation '{conversation_id}': {e}")
        return None

def read_all_conversations(container_client: CosmosClient, user_id: str) -> dict:
    """
    Retrieves all conversations for a specific user.

    Args:
        container_client (CosmosClient): The Cosmos DB container client.
        user_id (str): The ID of the user.

    Returns:
        dict: A dictionary of conversations where keys are conversation IDs and values are conversation content.
    """
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        items = list(container_client.query_items(query=query, enable_cross_partition_query=True))
        conversations = {item['id']: item['conversation_content'] for item in items}
        return conversations
    except Exception as e:
        print(f"Error reading all conversations for user '{user_id}': {e}")
        return {}

def read_all_conversations_ids_by_user(container_client: CosmosClient, user_id: str) -> pd.DataFrame:
    """
    Retrieves all conversation IDs, names, and last modified timestamps for a specific user.

    Args:
        container_client (CosmosClient): The Cosmos DB container client.
        user_id (str): The ID of the user.

    Returns:
        pd.DataFrame: A DataFrame with conversation IDs, names, and last modified timestamps.
    """
    try:
        query = f"""
        SELECT c.id, c.conversation_name, c.last_modified 
        FROM c 
        WHERE c.user_id = '{user_id}'
        ORDER BY c.last_modified DESC
        """

        # Execute the query
        items = list(container_client.query_items(query=query, enable_cross_partition_query=True))

        # Store conversations in a list of dictionaries
        user_conversations = [
            {'id': item['id'], 'conversation_name': item['conversation_name'], 'last_modified': item['last_modified']}
            for item in items
        ]

        # Convert list of dictionaries to a pandas DataFrame
        df_conversations_ids = pd.DataFrame(user_conversations)
        #df_conversations_ids.set_index('id', inplace=True)

        return df_conversations_ids
    except Exception as e:
        print(f"Error reading all conversation IDs for user '{user_id}': {e}")
        return pd.DataFrame()

def check_conversations_exists(container_client: CosmosClient, user_id: str) -> bool:
    """
    Checks if there are any conversations for a specific user.

    Args:
        container_client (CosmosClient): The Cosmos DB container client.
        user_id (str): The ID of the user.

    Returns:
        bool: True if conversations exist, otherwise False.
    """
    try:
        # Query to check for existing conversations for the user
        query = "SELECT VALUE COUNT(1) FROM c WHERE c.user_id = @user_id"
        parameters = [{"name": "@user_id", "value": user_id}]

        # Execute the query
        result = list(container_client.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        return result[0] > 0 if result else False
    except Exception as e:
        print(f"Error checking conversations for user '{user_id}': {e}")
        return False




def delete_conversation(container_client: CosmosClient, conversation_id: str, partition_key:str) -> None:
    """
    Deletes a conversation document from Cosmos DB based on the conversation ID.

    Args:
        container_client (ContainerClient): The Cosmos DB container client.
        conversation_id (str): The ID of the conversation to be deleted.

    Returns:
        None
    """
    try:
        # Primero, intenta obtener el documento para verificar si existe
        container_client.delete_item(item=conversation_id, partition_key=partition_key)

        print(f"Successfully deleted conversation '{conversation_id}'.")
    except Exception as e:
        print(f"Error deleting conversation '{conversation_id}': {e}")

