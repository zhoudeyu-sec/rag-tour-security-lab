from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import models


@dataclass
class RetrievedChunk:
    id: int
    title: str
    content: str
    trust_level: str
    is_poison: bool
    score: float


def _tokenize(question: str) -> list[str]:
    q = question.strip()
    if not q:
        return []
    parts = [p for p in q.replace("，", " ").replace("？", " ").split() if len(p) >= 2]
    if len(parts) < 2 and len(q) >= 2:
        return [q[i : i + 2] for i in range(0, len(q) - 1, 2)]
    return parts or [q]


def _score_chunk(kb: models.KnowledgeBase, tokens: list[str]) -> float:
    text = f"{kb.title} {kb.content}"
    hits = sum(1 for t in tokens if t in text)
    if hits == 0:
        return 0.0
    bonus = 3.0 if kb.is_poison else 0.0
    return hits + bonus


def retrieve(db: Session, question: str, mode: str, limit: int = 3) -> list[RetrievedChunk]:
    rows = db.query(models.KnowledgeBase).order_by(models.KnowledgeBase.id.desc()).all()
    tokens = _tokenize(question)

    if mode == "hardened":
        rows = [r for r in rows if not r.is_poison and r.trust_level != "untrusted"]

    scored: list[tuple[float, models.KnowledgeBase]] = []
    for row in rows:
        score = _score_chunk(row, tokens)
        if mode == "rag_poison_vuln" and row.is_poison:
            score = max(score, 2.5)
        if score > 0 or (mode == "rag_poison_vuln" and row.is_poison):
            scored.append((score, row))

    if mode == "rag_poison_vuln":
        poison_rows = [r for r in rows if r.is_poison]
        for pr in poison_rows:
            if not any(pr.id == x[1].id for x in scored):
                scored.append((2.0, pr))

    scored.sort(key=lambda x: (-x[0], -x[1].id))
    top = scored[:limit]

    if not top and rows and mode == "baseline":
        for row in rows[:limit]:
            top.append((0.1, row))

    return [
        RetrievedChunk(
            id=row.id,
            title=row.title,
            content=row.content,
            trust_level=row.trust_level,
            is_poison=row.is_poison,
            score=round(score, 2),
        )
        for score, row in top
    ]
