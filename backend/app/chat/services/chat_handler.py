import os
import pandas as pd
from azure_utils.keyvault import get_secret_value_from_keyvault
from azure_utils.cosmos import save_conversation, delete_conversation, setup_cosmos_client, read_all_conversations_ids_by_user, check_conversations_exists, read_conversation

AZ_KEYVAULT_URL = os.getenv('AZ_KEYVAULT_URL')
AZ_COSMOS_ACCOUNT_URL = os.getenv('AZ_COSMOS_ACCOUNT_URL')
AZ_COSMOS_CONTAINER_NAME = os.getenv('AZ_COSMOS_CONTAINER_NAME')
AZ_COSMOS_DATABASE_NAME = os.getenv('AZ_COSMOS_DATABASE_NAME')
AZ_COSMOS_ACCOUNT_KEY_SECRET_NAME = os.getenv('AZ_COSMOS_ACCOUNT_KEY_SECRET_NAME')

AZ_COSMOS_ACCOUNT_KEY = get_secret_value_from_keyvault(AZ_KEYVAULT_URL, AZ_COSMOS_ACCOUNT_KEY_SECRET_NAME)
container_cosmos_client = setup_cosmos_client( AZ_COSMOS_ACCOUNT_URL,AZ_COSMOS_ACCOUNT_KEY, AZ_COSMOS_DATABASE_NAME,AZ_COSMOS_CONTAINER_NAME)


class ChatManager:
    def __init__(self):
        self.container_client = container_cosmos_client

    def save_conversation(self, user_id, conversation_id, conversation_name, conversation_data):
        save_conversation(self.container_client, user_id, conversation_id, conversation_name, conversation_data)

    def delete_conversation(self, conversation_id, user_id):
        return delete_conversation(self.container_client, conversation_id, user_id)
    
    def read_all_conversations_ids_by_user(self, user_id):
        return read_all_conversations_ids_by_user(self.container_client, user_id)
    
    def check_conversations_exists(self, user_id):
        return check_conversations_exists(self.container_client, user_id)
    
    def read_conversation(self, conversation_id):
        return read_conversation(self.container_client, conversation_id) 
