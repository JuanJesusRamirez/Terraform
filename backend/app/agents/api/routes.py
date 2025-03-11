from fastapi import APIRouter
from app.agents.services.agent_handler import AgentHandler
from pydantic import BaseModel
from typing import List, Dict
from typing import Any

agent_handler = AgentHandler()
router = APIRouter()

class UserRequest(BaseModel):
    agent_name: str
    user_request: str
    prev_message: List[str]
    config: Dict[Any, Any]

    
@router.post("/agents/process_user_request")
async def process_user_request(request: UserRequest) -> Dict[str, Any]:
    """
    Invoke the agent graph with provided parameters
    """
    # Aquí solo invocas el servicio, no la lógica del agente directamente
    return agent_handler.execute_agent(request.agent_name, request.user_request, request.prev_message, request.config)

    
