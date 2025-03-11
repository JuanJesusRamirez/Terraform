from fastapi import APIRouter
from app.ms_auth.services.auth_ms_handler import MSAuthenticator
from pydantic import BaseModel

class Code(BaseModel):
    code: str
class AccessToken(BaseModel):
    access_token: str

ms_authenticator = MSAuthenticator()
router = APIRouter()

@router.get("/ms_auth/get_auth_url")
def get_auth_url():
    return ms_authenticator.get_auth_url()

@router.get("/ms_auth/get_logout_url")
def get_logout_url():
    return ms_authenticator.get_logout_url()

@router.get("/ms_auth/get_aida_url")
def get_aida_url(): 
    return ms_authenticator.get_aida_url()

@router.post("/ms_auth/get_token_from_code")
def get_token_from_code(request: Code):
    return ms_authenticator.get_token_from_code(request.code)

@router.post("/ms_auth/get_user_info")
def get_user_info(request: AccessToken):
    return ms_authenticator.get_user_info(request.access_token)



 