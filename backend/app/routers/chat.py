from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest
from app.services.chat_service import ask

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/ask")
async def ask_question(body: ChatRequest, db: Session = Depends(get_db)):
    data = await ask(db, body.question, body.user_id, body.mode)
    return {"code": 200, "message": "success", "data": data}
