import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import EvalRunRequest
from app.services.eval_service import run_eval

router = APIRouter(prefix="/api/v1/eval", tags=["eval"])


@router.post("/run")
async def eval_run(body: EvalRunRequest, db: Session = Depends(get_db)):
    report = await run_eval(db, body.dataset, body.mode, body.limit)
    return {"code": 200, "data": report}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    rows = db.query(models.EvalRun).order_by(models.EvalRun.id.desc()).limit(20).all()
    return {
        "code": 200,
        "data": [
            {
                "id": r.id,
                "lab_mode": r.lab_mode,
                "dataset": r.dataset,
                "total": r.total,
                "asr": r.asr,
                "attack_success": r.attack_success,
                "false_refusal": r.false_refusal,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    row = db.get(models.EvalRun, run_id)
    if not row:
        raise HTTPException(status_code=404, detail="run not found")
    return {"code": 200, "data": json.loads(row.report_json)}
