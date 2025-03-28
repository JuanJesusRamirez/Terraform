from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from msal import ConfidentialClientApplication
import os
import requests
from urllib.parse import urlencode
import jwt
from cryptography.fernet import Fernet

app = FastAPI()

CLIENT_ID = os.getenv("AZ_CLIENT_ID_MS_AUTH")
CLIENT_SECRET = os.getenv("AZ_CLIENT_SECRET_MS_AUTH")
TENANT_ID = os.getenv("Az_TENANT_ID_MS_AUTH")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REDIRECT_AIDA = os.getenv('REDIRECT_AIDA')

# Change from tenant-specific to multi-tenant authority
# authority = f"https://login.microsoftonline.com/{TENANT_ID}"
authority = "https://login.microsoftonline.com/common"  # For any Microsoft account (personal and work)
# Or use "organizations" for work accounts only: authority = "https://login.microsoftonline.com/organizations"

# List of allowed domains (optional)
ALLOWED_DOMAINS = ['flar.net']  # Add all domains you want to allow

SCOPE = ['User.Read']

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
fernet_key = os.environ.get("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(fernet_key)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=authority,
    client_credential=CLIENT_SECRET,
)

class MSAuthenticator:
    def __init__(self):
        self.msal_app = msal_app

    def get_auth_url(self):
        return self.msal_app.get_authorization_request_url(scopes=SCOPE, redirect_uri=REDIRECT_URI)

    def get_logout_url(self):
        params = {'post_logout_redirect_uri': REDIRECT_URI}
        return f'https://login.microsoftonline.com/common/oauth2/v2.0/logout?{urlencode(params)}'

    def get_aida_url(self):
        return REDIRECT_AIDA

    def get_token_from_code(self, code):
        token_data = self.msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
        token_str = token_data.get("access_token")
        
        if not token_str:
            raise HTTPException(status_code=400, detail="No access_token in response.")
            
        # Validate tenant/domain if needed
        if ALLOWED_DOMAINS and len(ALLOWED_DOMAINS) > 0:
            # Get user info to check domain
            headers = {'Authorization': f'Bearer {token_str}'}
            user_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
            user_data = user_response.json()
            
            # Check if user's domain is in allowed domains
            user_email = user_data.get('userPrincipalName', '')
            domain = user_email.split('@')[-1] if '@' in user_email else None
            
            if domain not in ALLOWED_DOMAINS:
                raise HTTPException(status_code=403, detail=f"Access denied. Domain {domain} not authorized.")
        
        encrypted_token = fernet.encrypt(token_str.encode()).decode()
        jwt_token = jwt.encode({"token": encrypted_token}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": jwt_token}
        
    def get_user_info(self, token):
        decoded = verify_jwt_token(token)
        decrypted_token = fernet.decrypt(decoded["token"].encode()).decode()
        headers = {'Authorization': f'Bearer {decrypted_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        return response.json()
