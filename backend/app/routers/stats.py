import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/overview")
def stats_overview(db: Session = Depends(get_db)):
    total_logs = db.query(func.count(models.ConversationLog.id)).scalar() or 0
    total_eval = db.query(func.count(models.EvalRun.id)).scalar() or 0
    avg_ms = db.query(func.avg(models.ConversationLog.response_time)).scalar()

    by_mode = (
        db.query(
            models.ConversationLog.lab_mode,
            func.count(models.ConversationLog.id),
            func.avg(models.ConversationLog.response_time),
        )
        .group_by(models.ConversationLog.lab_mode)
        .all()
    )

    mode_stats = []
    for mode, cnt, avg_rt in by_mode:
        tagged = (
            db.query(models.ConversationLog)
            .filter(
                models.ConversationLog.lab_mode == mode,
                models.ConversationLog.attack_success.isnot(None),
            )
            .all()
        )
        attack_n = len(tagged)
        attack_ok = sum(1 for x in tagged if x.attack_success)
        mode_stats.append(
            {
                "lab_mode": mode,
                "conversations": cnt,
                "avg_response_time_ms": round(float(avg_rt or 0), 1),
                "eval_tagged_cases": attack_n,
                "eval_attack_success": attack_ok,
                "eval_asr": round(attack_ok / attack_n, 4) if attack_n else None,
            }
        )

    recent_eval = (
        db.query(models.EvalRun).order_by(models.EvalRun.id.desc()).limit(5).all()
    )

    return {
        "code": 200,
        "data": {
            "total_conversations": total_logs,
            "total_eval_runs": total_eval,
            "avg_response_time_ms": round(float(avg_ms or 0), 1),
            "by_mode": mode_stats,
            "recent_eval_runs": [
                {
                    "id": r.id,
                    "lab_mode": r.lab_mode,
                    "dataset": r.dataset,
                    "total": r.total,
                    "asr": r.asr,
                    "false_refusal": r.false_refusal,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent_eval
            ],
        },
    }


@router.get("/summary")
def stats_summary(
    lab_mode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """按模式汇总：对话数、检索到投毒比例、拒绝比例、评测 ASR（若有标注）"""
    q = db.query(models.ConversationLog)
    if lab_mode:
        q = q.filter(models.ConversationLog.lab_mode == lab_mode)
    rows = q.all()
    n = len(rows)
    if n == 0:
        return {"code": 200, "data": {"count": 0, "message": "暂无记录，请先进行问答或评测"}}

    poison_hit = sum(1 for r in rows if r.retrieved_poison)
    refused = sum(1 for r in rows if r.refused)
    tagged = [r for r in rows if r.attack_success is not None]
    attack_ok = sum(1 for r in tagged if r.attack_success)

    return {
        "code": 200,
        "data": {
            "lab_mode": lab_mode or "all",
            "conversation_count": n,
            "poison_retrieval_rate": round(poison_hit / n, 4),
            "refusal_rate": round(refused / n, 4),
            "avg_response_time_ms": round(sum(r.response_time or 0 for r in rows) / n, 1),
            "eval_tagged_count": len(tagged),
            "eval_attack_success": attack_ok,
            "eval_asr": round(attack_ok / len(tagged), 4) if tagged else None,
        },
    }
