import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import get_settings
from app.database import get_db
from app.rag.prompt import build_system_prompt
from app.rag.retriever import retrieve
from app.seed import seed_database
from app.services.chat_service import resolve_mode

router = APIRouter(prefix="/api/v1/lab", tags=["lab"])


def verify_lab_token(x_lab_token: str | None = Header(default=None)):
    token = get_settings().lab_admin_token
    if token and x_lab_token != token:
        raise HTTPException(status_code=401, detail="Invalid lab token")


@router.get("/mode")
def get_mode():
    s = get_settings()
    return {
        "code": 200,
        "data": {
            "lab_mode": s.lab_mode,
            "llm_configured": s.llm_configured,
            "use_mock_llm": s.use_mock_llm or not s.llm_configured,
        },
    }


@router.post("/mode")
def set_mode(body: schemas.LabModeSet, _: None = Depends(verify_lab_token)):
    mode = body.mode.strip()
    if mode not in ("baseline", "rag_poison_vuln", "hardened"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    os.environ["LAB_MODE"] = mode
    get_settings.cache_clear()
    return {"code": 200, "message": f"LAB_MODE={mode}（当前进程内生效，重启后请改 .env）"}


@router.post("/seed")
def seed_kb(reset: bool = False, db: Session = Depends(get_db), _: None = Depends(verify_lab_token)):
    return {"code": 200, "data": seed_database(db, reset=reset)}


@router.post("/poison")
def inject_poison(body: schemas.PoisonInject, db: Session = Depends(get_db), _: None = Depends(verify_lab_token)):
    row = models.KnowledgeBase(
        title=body.title,
        content=body.content,
        category=body.category,
        trust_level="untrusted",
        is_poison=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"code": 200, "data": row}


@router.post("/retrieve")
def preview_retrieve(body: schemas.RetrievePreviewRequest, db: Session = Depends(get_db)):
    mode = resolve_mode(body.mode)
    chunks = retrieve(db, body.question, mode)
    return {
        "code": 200,
        "data": {
            "mode": mode,
            "chunks": [c.__dict__ for c in chunks],
            "system_prompt_preview": build_system_prompt(chunks, mode)[:2000],
        },
    }
