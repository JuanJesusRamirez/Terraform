import os
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import jwt
from cryptography.fernet import Fernet
from UI_Pages import agent_pag, file_upload_pag
from front_utils import BaseAPIClient, wait_for_backend

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
fernet_key = os.environ.get("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(fernet_key)


API_URL = os.environ.get("BACKEND_API_URL")

class APIClient(BaseAPIClient):
    """Base class using the enhanced BaseAPIClient with retry mechanism."""
    pass

class AuthService:
    def __init__(self, api_client, secret_key, algorithm):
        self.api_client = api_client
        self.secret_key = secret_key
        self.algorithm = algorithm

    def verify_jwt(self, token):
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def get_token_from_code(self, code): 
        return self.api_client._post("/api/ms_auth/get_token_from_code", json={"code": code})

    def get_auth_urls(self):
        try:
            aida_url = self.api_client._get("/api/ms_auth/get_aida_url")
            auth_url = self.api_client._get("/api/ms_auth/get_auth_url")
            return aida_url, auth_url
        except Exception as e:
            # Show waiting message if backend is not ready
            if wait_for_backend("Initializing authentication service..."):
                # Try again after backend is available
                aida_url = self.api_client._get("/api/ms_auth/get_aida_url")
                auth_url = self.api_client._get("/api/ms_auth/get_auth_url")
                return aida_url, auth_url
            return {"error": "Service unavailable"}, {"error": "Service unavailable"}

    def get_user_info(self, access_token):
        return self.api_client._post("/api/ms_auth/get_user_info", json={"access_token": access_token})

class AuthHandler:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def handle_authentication(self):
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False

        query_params = st.query_params
        if 'code' in query_params:
            try:
                result = self.auth_service.get_token_from_code(query_params['code'])
                if 'access_token' in result:
                    decoded = self.auth_service.verify_jwt(result['access_token'])
                    st.session_state.access_token = result['access_token']
                    st.session_state.is_authenticated = True
                    return True
            except Exception as e:
                st.error(f"Error during authentication: {str(e)}")

        if not st.session_state.is_authenticated:
            aida_url, auth_url = self.auth_service.get_auth_urls()
            self.display_auth_buttons(auth_url, aida_url)
            return False
        return True

    def display_auth_buttons(self, auth_url, aida_url):
        st.markdown(f'''
        <div style="text-align: center;">
            <div style="text-align: center">
                We recommend using Microsoft Edge for easier authentication.
            </div>
            <br>
            <a href="{auth_url}" target="_self" style="text-decoration:none;">
                <button style="padding:10px 20px; font-size:16px; width:20%; 
                        background-color: #4CAF50; color: white; 
                        border: none; border-radius: 5px;">
                    🔑 Login with Microsoft
                </button>
            </a>
           
        </div>
        ''', unsafe_allow_html=True)
        st.write('-')

class PageConfigurator:
    @staticmethod
    def configure_page():
        st.set_page_config(
            page_title="RALF",
            page_icon="🤖",
            layout="wide"
        )

        st.markdown(
            """
            <style>
            .title {
                text-align: center;
            }
            </style>
            <h3 class="title">RALF - Secular Forum</h3>
            """,
            unsafe_allow_html=True
        )

class SidebarConfigurator:
    def __init__(self, auth_service, auth_handler):
        self.auth_service = auth_service
        self.auth_handler = auth_handler

    def configure_sidebar(self):
        with st.sidebar:
            if st.session_state.get('access_token'):
                st.sidebar.title("RALF")
                user_info = self.auth_service.get_user_info(st.session_state['access_token'])
                st.session_state.user_name = user_info.get('displayName', "User")
                st.session_state.user_id = user_info.get('id', None)

                st.markdown(f'''
                <div style="text-align: center;">
                    <h2 style="font-size: 20px;">{st.session_state.user_name} 🟢</h2>
                </div>
                ''', unsafe_allow_html=True)

                st.session_state.selected_page = option_menu(
                    menu_title="",
                    options=["Chats", "File Upload"],
                    icons=["robot", "database"],
                    menu_icon="bar-chart-fill",
                    default_index=0,
                )
            else:
                self.auth_handler.handle_authentication()

def main():
    PageConfigurator.configure_page()
    api_client = APIClient(API_URL)
    auth_service = AuthService(api_client, SECRET_KEY, ALGORITHM)
    auth_handler = AuthHandler(auth_service)
    sidebar_configurator = SidebarConfigurator(auth_service, auth_handler)

    if auth_handler.handle_authentication():
        sidebar_configurator.configure_sidebar()

        if st.session_state.get('selected_page') == "Chats":
            agent_pag.run()
        elif st.session_state.get('selected_page') == "File Upload":
            file_upload_pag.run()

if __name__ == "__main__":
    main()