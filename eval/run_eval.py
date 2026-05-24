#!/usr/bin/env python3
"""本地评测 CLI：在 backend 目录执行 python ../eval/run_eval.py --mode baseline"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed import seed_database  # noqa: E402
from app.services.eval_service import run_eval  # noqa: E402


async def main():
    parser = argparse.ArgumentParser(description="AI Tour Guide Lab Eval Runner")
    parser.add_argument("--mode", default="baseline", choices=["baseline", "rag_poison_vuln", "hardened"])
    parser.add_argument("--dataset", default="all", help="all | benign_qa | indirect_injection | rag_poison")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--reset-kb", action="store_true")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if args.reset_kb:
            seed_database(db, reset=True)
        else:
            seed_database(db)
        report = await run_eval(db, args.dataset, args.mode, args.limit)
        out = BACKEND.parent / "eval" / "reports" / f"report_{args.mode}_{report['run_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Mode: {report['lab_mode']}")
        print(f"ASR: {report['asr']:.1%} ({report['attack_success']}/{report['attack_cases']})")
        print(f"False refusal rate: {report['false_refusal_rate']:.1%}")
        print(f"Report: {out}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
