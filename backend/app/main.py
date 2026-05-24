import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.db_migrate import migrate_conversation_logs
from app.routers import chat, eval, kb, lab, logs, stats
from app.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
migrate_conversation_logs()

app = FastAPI(
    title="AI Tour Guide Security Lab",
    description="景区导游 RAG 应用 — AI 安全红队评测靶场（baseline / rag_poison_vuln / hardened）",
    version="2.0.0-lab",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(kb.router)
app.include_router(lab.router)
app.include_router(eval.router)
app.include_router(logs.router)
app.include_router(stats.router)


@app.get("/api/v1/health")
def health():
    return {"code": 200, "status": "ok"}


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        info = seed_database(db)
        logger.info("KB seed: %s", info)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
