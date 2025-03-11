import streamlit as st
import requests
import pandas as pd
import random
import os

from front_utils import log_function, create_chat_excel, BaseAPIClient, wait_for_backend

API_URL = os.environ.get("BACKEND_API_URL")

class APIClient(BaseAPIClient):
    """Handles connection with the FastAPI using the base client with retry mechanism."""
    pass


class AgentClient(APIClient):
    """Handles connection with the FastAPI for user requests."""
    def process_user_request(self, agent_name, user_request, prev_message, config):
        """Sends a POST request to the API with the user's input."""
        payload = {
            "agent_name": agent_name,
            "user_request": user_request,
            "prev_message": prev_message,
            "config": config
        }

        return self._post("/api/agents/process_user_request", json=payload)


class ConversationManagerClient(APIClient):
    """Class to handle connection with the FastAPI for conversation management."""
    def read_all_conversations_ids_by_user(self, user_id):
        """Gets all conversation IDs for a user and converts them into a DataFrame."""
        response = self._post("/api/conversation_manager/read_all_conversations_ids_by_user", json={"user_id": user_id})
        if "error" in response:
            if "Backend service is not available" in response["error"]:
                st.warning("Waiting for backend services to initialize...")
                if wait_for_backend("Initializing backend services..."):
                    # Retry after successful wait
                    response = self._post("/api/conversation_manager/read_all_conversations_ids_by_user", json={"user_id": user_id})
                    if "error" not in response:
                        return pd.DataFrame(response)
            return pd.DataFrame()  # Returns an empty DataFrame in case of error
        return pd.DataFrame(response)

    def check_conversations_exists(self, user_id):
        """Checks if conversations exist for a user."""
        return self._post("/api/conversation_manager/check_conversations_exists", json={"user_id": user_id})

    def save_conversation(self, user_id, conversation_id, conversation_name, conversation_content):
        """Saves a conversation in the database."""
        payload = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "conversation_name": conversation_name,
            "conversation_content": conversation_content
        }
        return self._post("/api/conversation_manager/save_conversation", json=payload)

    def delete_conversation(self, conversation_id, user_id):
        """Deletes a conversation from the database."""
        return self._post("/api/conversation_manager/delete_conversation", json={"conversation_id": conversation_id, "user_id": user_id})

    def read_conversation(self, conversation_id):
        """Reads a conversation from the database."""
        return self._post("/api/conversation_manager/read_conversation", json={"conversation_id": conversation_id})


class ConversationService:
    """Service class to handle conversation-related operations."""
    def __init__(self, conversation_manager_client):
        self.conversation_manager_client = conversation_manager_client

    def generate_conversation_id(self, df: pd.DataFrame, user_id: str) -> str:
        """Generates a new conversation ID based on existing IDs."""
        try:
            df = df.reset_index()
            df['id_cov'] = df['id'].apply(lambda x: x.split('-')[-1]).astype(int)
            max_value = df['id_cov'].max()
            while True:
                new_id = random.randint(0, 99999)
                if new_id not in df['id_cov'].values:
                    break
 
            return f"{user_id}-{str(new_id).zfill(5)}"
        except Exception as e:
            print(f"Error generating new conversation ID for user '{user_id}': {e}")
            return f"{user_id}-00000"

    def create_conversation(self, user_id, new_conversation_name, conversation_exist, conversations):
        """Creates a new conversation."""
        if new_conversation_name not in st.session_state.conversation_list:
            if conversation_exist:
                current_conversation_id = self.generate_conversation_id(conversations, user_id)
            else:
                current_conversation_id = f'{user_id}-00000'
            st.session_state.conversations[current_conversation_id] = {"name": new_conversation_name, "messages": []}
            st.session_state.new_conversation = {
                "user_id": user_id,
                "conversation_id": current_conversation_id,
                "conversation_name": new_conversation_name,
                "conversation_content": []
            }
            self.conversation_manager_client.save_conversation(user_id, current_conversation_id, new_conversation_name, [])
            st.success(f"Conversation '{new_conversation_name}' created successfully.")
            st.session_state.conversation_list.append(new_conversation_name)
            st.rerun()
        else:
            st.warning("Please enter a valid and unique name for the conversation before proceeding.")

    def select_conversation(self, conversation_exist, conversations):
        """Selects an existing conversation."""
        if conversation_exist:
            st.session_state.conversation_list = conversations['conversation_name'].tolist()
            st.session_state.current_conversation_name = st.selectbox("My chats", st.session_state.conversation_list)
            st.session_state.current_conversation_id = conversations.loc[conversations['conversation_name'] == st.session_state.current_conversation_name, 'id'].values[0]
        else:
            st.warning("No conversations available. Create a new one.")


def init_state_variables():
    """Initialize session state variables if they do not exist."""
    defaults = {
        "conversations": {},
        "conversation_exist": False,
        "conversation_list": [],
        "conversation_content": {},
        "conversation_messages": None,
        "excel_data": None,
        "conversation_name": None,
        "current_conversation_name": None,
        "current_conversation_id": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def run():
    """Main function to run the Streamlit app."""
    st.markdown("##### Chat Assistant")
    init_state_variables()
    conversation_manager_client = ConversationManagerClient()
    agent_client = AgentClient()
    conversation_service = ConversationService(conversation_manager_client)

    st.session_state.conversation_exist = conversation_manager_client.check_conversations_exists(st.session_state.user_id)
    if st.session_state.conversation_exist:
        st.session_state.conversations = conversation_manager_client.read_all_conversations_ids_by_user(st.session_state.user_id)

    with st.sidebar:
        l1, l2, l3 = st.columns([3, 0.5, 3])
        with l1:
            st.session_state.new_conversation_name = st.text_input("New chat:", key="new_conversation_name_key", value='Enter a new name')
            if st.button("➕ Create new chat"):
                conversation_service.create_conversation(st.session_state.user_id, st.session_state.new_conversation_name, st.session_state.conversation_exist, st.session_state.conversations)
        with l3:
            conversation_service.select_conversation(st.session_state.conversation_exist, st.session_state.conversations)
            if st.session_state.conversation_exist:
                if st.button("🗑️ Delete current chat"):
                    conversation_manager_client.delete_conversation(st.session_state.current_conversation_id, st.session_state.user_id)
                    st.session_state.conversation_content[st.session_state.current_conversation_id]["messages"] = []
                    st.rerun()
        

        if st.session_state.current_conversation_id:
            st.session_state.conversation_content[st.session_state.current_conversation_id] = {
                "name": st.session_state.current_conversation_name,
                "messages": conversation_manager_client.read_conversation(st.session_state.current_conversation_id) or []
            }
            if st.session_state.current_conversation_id is not None:
                st.session_state.excel_data = create_chat_excel(st.session_state.conversation_content[st.session_state.current_conversation_id]["messages"])
        
        with l3:
            if st.session_state.current_conversation_id is not None:
                st.download_button(
                    label="➡️ Export to Excel",
                    data=st.session_state.excel_data,
                    file_name=st.session_state.current_conversation_name + '.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
        st.markdown("---")
        log_function()
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.write(""" -- 1.5.0 --""")
    if st.session_state.current_conversation_id is not None:     
        st.session_state.conversation_messages = st.session_state.conversation_content[st.session_state.current_conversation_id]
        if "messages" in st.session_state.conversation_messages and st.session_state.conversation_exist:
            for message in st.session_state.conversation_messages["messages"]:
                with st.chat_message(message["role"]):
                    content = message.get("content", None)
                    if content:
                        st.markdown(content)

        if st.session_state.conversation_exist:
            st.session_state.user_input = st.chat_input("Type your question here...")

        if st.session_state.user_input:
            if st.session_state.current_conversation_id in st.session_state.conversation_content:
                st.session_state.conversation_messages = st.session_state.conversation_content[st.session_state.current_conversation_id]
                if "messages" not in st.session_state.conversation_messages or st.session_state.conversation_messages["messages"] is None:
                    st.session_state.conversation_messages["messages"] = []
                st.session_state.conversation_messages["messages"].append({"role": "user", "content": st.session_state.user_input})
                

                
                with st.chat_message("user"):
                    st.markdown(st.session_state.user_input)
                    
                    
                with st.chat_message("assistant"):
                    agent_name = "agent_a"
    
                    config = {
                        "configurable": {
                            "thread_id": st.session_state.current_conversation_id
                        }
                    }
                    messages_content = [msg['content'] for msg in st.session_state.conversation_content[st.session_state.current_conversation_id]["messages"][:-1]]
                    response_dict  = agent_client.process_user_request(agent_name, st.session_state.user_input, messages_content, config)
                    combined_message = response_dict["response"]
                    input_tokens = response_dict["input_tokens"]
                    output_tokens = response_dict["output_tokens"]
                    combined_message2 = combined_message+ f"\n\n---\nInput Tokens: {input_tokens}  <->  Output Tokens: {output_tokens}"
                    st.markdown(combined_message2)
            
                st.session_state.conversation_content[st.session_state.current_conversation_id]["messages"].append({"role": "assistant", "content": combined_message})
                conversation_manager_client.save_conversation(st.session_state.user_id, st.session_state.current_conversation_id, st.session_state.current_conversation_name, st.session_state.conversation_content[st.session_state.current_conversation_id]["messages"])
