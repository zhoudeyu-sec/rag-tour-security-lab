from typing import Any, Optional

from pydantic import BaseModel, Field


class KBBase(BaseModel):
    title: str
    content: str
    category: str = "general"
    trust_level: str = "trusted"
    is_poison: bool = False


class KBResponse(KBBase):
    id: int

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: str = "guest"
    question: str
    mode: Optional[str] = None


class ChatResponseData(BaseModel):
    answer: str
    log_id: int
    response_time: str
    lab_mode: str
    retrieved: list[dict[str, Any]]


class LabModeSet(BaseModel):
    mode: str


class PoisonInject(BaseModel):
    title: str = "恶意知识条目"
    content: str
    category: str = "attack"


class EvalRunRequest(BaseModel):
    dataset: str = "all"
    mode: Optional[str] = None
    limit: Optional[int] = None


class RetrievePreviewRequest(BaseModel):
    question: str
    mode: Optional[str] = None
