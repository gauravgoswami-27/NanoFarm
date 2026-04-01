from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.chat_service import chat_service
from typing import List, Optional

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    parts: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None

@router.post("/chat-agronomist")
async def chat_agronomist(req: ChatRequest):
    try:
        # Compatibility layer: converting Pydantic history objects back to simple list
        history_list = []
        if req.history:
           for h in req.history:
              history_list.append({"role": h.role, "parts": [h.parts]})
        
        reply = await chat_service.get_chat_response(req.message, history=history_list)
        
        return {
            "status": "success",
            "type": "chatbot_response",
            "data": {
                "chatbot_response": reply
            }
        }
    except Exception as e:
        print(f"❌ Chat Router Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
