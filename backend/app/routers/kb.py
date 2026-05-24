from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/v1/kb", tags=["kb"])


@router.get("/list")
def list_kb(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.KnowledgeBase)
    if keyword:
        q = q.filter(models.KnowledgeBase.title.contains(keyword))
    total = q.count()
    items = q.order_by(models.KnowledgeBase.id.desc()).offset(skip).limit(limit).all()
    return {"code": 200, "data": {"items": items, "total": total}}


@router.post("/add")
def add_kb(item: schemas.KBBase, db: Session = Depends(get_db)):
    row = models.KnowledgeBase(**item.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"code": 200, "message": "添加成功", "data": row}
