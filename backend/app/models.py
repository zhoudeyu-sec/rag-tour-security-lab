import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    trust_level = Column(String(32), default="trusted")
    is_poison = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), default="guest")
    question = Column(Text)
    answer = Column(Text)
    response_time = Column(Integer)
    lab_mode = Column(String(32))
    retrieved_ids = Column(String(255))
    retrieved_poison = Column(Boolean, nullable=True)
    refused = Column(Boolean, nullable=True)
    attack_success = Column(Boolean, nullable=True)
    case_id = Column(String(64), nullable=True)
    source = Column(String(32), default="chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    lab_mode = Column(String(32))
    dataset = Column(String(64))
    total = Column(Integer)
    attack_success = Column(Integer)
    false_refusal = Column(Integer)
    asr = Column(Float)
    report_json = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
