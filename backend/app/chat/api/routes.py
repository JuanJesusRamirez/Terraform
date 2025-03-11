
from fastapi import APIRouter, HTTPException, Request
from app.chat.services.chat_handler import ChatManager
from pydantic import BaseModel
from typing import List, Dict

chat_manager= ChatManager()
router = APIRouter()

# Define the Pydantic model
class Conversation(BaseModel):
    user_id: str
    conversation_id: str
    conversation_name: str
    conversation_content: List[Dict]

class UserId(BaseModel):
    user_id: str
    
class ConversationId(BaseModel):
    conversation_id: str
class DeleteConversationId(BaseModel):
    conversation_id: str
    user_id: str


@router.post("/conversation_manager/save_conversation")
async def save_conversation(request: Conversation):
    """
    Save a conversation with provided parameters
    """
    try:
        # Access data directly from the Pydantic model
        user_id = request.user_id
        conversation_id = request.conversation_id
        conversation_name = request.conversation_name
        conversation_content = request.conversation_content

        # Simulate saving the conversation
        chat_manager.save_conversation(user_id, conversation_id, conversation_name, conversation_content)
        return {"message": "Conversation saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation_manager/read_all_conversations_ids_by_user")
async def read_all_conversations_ids_by_user(request: UserId) -> dict():
    """
    Invoke the agent graph with provided parameters
    """
    # Aquí solo invocas el servicio, no la lógica del agente directamente
    result = chat_manager.read_all_conversations_ids_by_user(request.user_id)
    return result.to_dict(orient="records")


@router.post("/conversation_manager/check_conversations_exists")
async def check_conversations_exists(request: UserId) -> dict():
    """
    Invoke the agent graph with provided parameters
    """
    # Aquí solo invocas el servicio, no la lógica del agente directamente
    return chat_manager.check_conversations_exists(request.user_id)

@router.post("/conversation_manager/read_conversation")
async def read_conversation(request: ConversationId) -> dict():
    """
    Invoke the agent graph with provided parameters
    """
    # Aquí solo invocas el servicio, no la lógica del agente directamente
    return chat_manager.read_conversation(request.conversation_id)

@router.post("/conversation_manager/delete_conversation")
async def delete_conversation(request: DeleteConversationId) -> dict():
    """
    Invoke the agent graph with provided parameters
    """
    # Aquí solo invocas el servicio, no la lógica del agente directamente
    return chat_manager.delete_conversation(request.conversation_id, request.user_id)
