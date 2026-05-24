import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


def _log_item(row: models.ConversationLog) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "question": row.question,
        "answer": row.answer,
        "response_time_ms": row.response_time,
        "lab_mode": row.lab_mode,
        "retrieved_ids": row.retrieved_ids,
        "retrieved_poison": row.retrieved_poison,
        "refused": row.refused,
        "attack_success": row.attack_success,
        "case_id": row.case_id,
        "source": row.source,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/list")
def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    lab_mode: Optional[str] = None,
    source: Optional[str] = None,
    case_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.ConversationLog)
    if lab_mode:
        q = q.filter(models.ConversationLog.lab_mode == lab_mode)
    if source:
        q = q.filter(models.ConversationLog.source == source)
    if case_id:
        q = q.filter(models.ConversationLog.case_id == case_id)
    total = q.count()
    items = q.order_by(models.ConversationLog.id.desc()).offset(skip).limit(limit).all()
    return {"code": 200, "data": {"items": [_log_item(x) for x in items], "total": total}}


@router.get("/export")
def export_logs(
    lab_mode: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.ConversationLog).order_by(models.ConversationLog.id.asc())
    if lab_mode:
        q = q.filter(models.ConversationLog.lab_mode == lab_mode)
    if source:
        q = q.filter(models.ConversationLog.source == source)
    rows = q.all()
    payload = {
        "exported": len(rows),
        "items": [_log_item(x) for x in rows],
    }
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": "attachment; filename=conversation_logs.json"},
    )
