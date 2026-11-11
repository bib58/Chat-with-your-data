import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _database_url() -> str:
    default_path = os.path.join(os.path.dirname(__file__), "feedback.db")
    configured_url = os.getenv("FEEDBACK_DATABASE_URL", "").strip()
    return configured_url or f"sqlite:///{default_path}"


engine = create_engine(
    _database_url(),
    connect_args={"check_same_thread": False} if _database_url().startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_feedback_database() -> None:
    Base.metadata.create_all(bind=engine)


def save_feedback(
    *,
    message_id: str,
    trace_id: Optional[str],
    rating: int,
    query: Optional[str],
    response: Optional[str],
    reason: Optional[str],
    comment: Optional[str],
) -> Feedback:
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        feedback = session.query(Feedback).filter_by(message_id=message_id).one_or_none()
        if feedback is None:
            feedback = Feedback(
                message_id=message_id,
                created_at=now,
            )
            session.add(feedback)

        feedback.trace_id = trace_id
        feedback.query = query
        feedback.response = response
        feedback.rating = rating
        feedback.reason = reason
        feedback.comment = comment
        feedback.updated_at = now
        session.commit()
        session.refresh(feedback)
        return feedback


def submit_langsmith_feedback(trace_id: Optional[str], rating: int, reason: Optional[str], comment: Optional[str]) -> None:
    if not trace_id or not os.getenv("LANGSMITH_API_KEY"):
        return

    try:
        from langsmith import Client

        Client().create_feedback(
            run_id=trace_id,
            key="user_rating",
            score=1 if rating == 1 else 0,
            comment=comment,
            extra={"reason": reason} if reason else None,
        )
    except Exception:
        logger.warning("LangSmith feedback submission failed for trace %s", trace_id, exc_info=True)
