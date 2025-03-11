from urllib.parse import urlencode  # To encode parameters in URLs
import requests  # To make HTTP requests

import streamlit as st  # To build the web application interface
from datetime import datetime, timedelta  # To handle date and time operations
from typing import Optional, Dict, Any

def get_logout_url(REDIRECT_URI: str) -> str:
    """
    Generate the logout URL with the specified redirect URI.

    Args:
        REDIRECT_URI (str): The URI to redirect to after logout.

    Returns:
        str: The generated logout URL, or an empty string if an error occurs.
    """
    try:
        params = {'post_logout_redirect_uri': REDIRECT_URI}
        return f'https://login.microsoftonline.com/common/oauth2/v2.0/logout?{urlencode(params)}'
    except Exception as e:
        st.error(f"Error generating logout URL: {e}")
        return ''

def get_user_info(access_token: str) -> Dict[str, Any]:
    """
    Retrieve user information from Microsoft Graph API using the access token.

    Args:
        access_token (str): The access token to authenticate the request.

    Returns:
        Dict[str, Any]: A dictionary containing user information, or an empty dictionary if an error occurs.
    """
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error retrieving user information: {e}")
        return {}

def get_auth_url(app: Any, SCOPE: str, REDIRECT_URI: str) -> str:
    """
    Generate the authorization URL to start the authentication process.

    Args:
        app (Any): The application instance used for generating the auth URL.
        SCOPE (str): The scope of the authorization request.
        REDIRECT_URI (str): The URI to redirect to after authorization.

    Returns:
        str: The generated authorization URL, or an empty string if an error occurs.
    """
    try:
        return app.get_authorization_request_url(scopes=SCOPE, redirect_uri=REDIRECT_URI)
    except Exception as e:
        st.error(f"Error generating authorization URL: {e}")
        return ''

def get_token_from_code(app: Any, code: str, SCOPE: str, REDIRECT_URI: str) -> Dict[str, Any]:
    """
    Exchange the authorization code for an access token.

    Args:
        app (Any): The application instance used for exchanging the code.
        code (str): The authorization code to exchange.
        SCOPE (str): The scope of the authorization request.
        REDIRECT_URI (str): The URI to redirect to after authorization.

    Returns:
        Dict[str, Any]: A dictionary containing the access token and other information, or an empty dictionary if an error occurs.
    """
    try:
        result = app.acquire_token_by_authorization_code(
            code, scopes=SCOPE, redirect_uri=REDIRECT_URI
        )
        return result
    except Exception as e:
        st.error(f"Error exchanging authorization code for token: {e}")
        return {}

def refresh_token(app: Any, SCOPE: str) -> None:
    """
    Refresh the access token using the refresh token stored in session state.

    Args:
        app (Any): The application instance used for refreshing the token.
        SCOPE (str): The scope of the token refresh request.

    Returns:
        None
    """
    try:
        if 'refresh_token' in st.session_state:
            result = app.acquire_token_by_refresh_token(
                st.session_state['refresh_token'], scopes=SCOPE
            )
            if 'access_token' in result:
                st.session_state['access_token'] = result['access_token']
                st.session_state['expires_at'] = datetime.utcnow() + timedelta(seconds=result['expires_in'])
            else:
                st.error("No se pudo refrescar el token.")
    except Exception as e:
        st.error(f"Error refreshing token: {e}")

