import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    __table_args__ = (UniqueConstraint("message_id", name="uq_user_feedback_message_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    message_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    feedback_type: Mapped[str] = mapped_column(String(32), nullable=False)
    feedback_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _database_url() -> Optional[str]:
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if not configured_url:
        return None
    if configured_url.startswith("postgres://"):
        return "postgresql+psycopg://" + configured_url[len("postgres://"):]
    if configured_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + configured_url[len("postgresql://"):]
    return configured_url


engine = None
SessionLocal = None


def _get_session_factory():
    global engine, SessionLocal
    if SessionLocal is not None:
        return SessionLocal

    database_url = _database_url()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
        return SessionLocal
    except Exception as exc:
        logger.error("Unable to configure the Neon feedback database.")
        raise RuntimeError("Unable to configure the Neon feedback database.") from exc


def initialize_feedback_database() -> bool:
    if not _database_url():
        logger.warning("DATABASE_URL is not configured; feedback storage is disabled.")
        return False

    try:
        session_factory = _get_session_factory()
        Base.metadata.create_all(bind=session_factory.kw["bind"])
        return True
    except Exception:
        logger.error("Unable to initialize the Neon feedback database.")
        return False


def save_feedback(
    *,
    question: str,
    answer: str,
    session_id: Optional[str],
    message_id: str,
    feedback_type: str,
    feedback_reason: Optional[str],
) -> UserFeedback:
    now = datetime.now(timezone.utc)
    session_factory = _get_session_factory()
    with session_factory() as session:
        feedback = session.query(UserFeedback).filter_by(message_id=message_id).one_or_none()
        if feedback is None:
            feedback = UserFeedback(
                question=question,
                answer=answer,
                session_id=session_id,
                message_id=message_id,
                feedback_type=feedback_type,
                feedback_reason=feedback_reason,
                created_at=now,
            )
            session.add(feedback)
        else:
            feedback.question = question
            feedback.answer = answer
            feedback.session_id = session_id
            feedback.feedback_type = feedback_type
            feedback.feedback_reason = feedback_reason
        session.commit()
        session.refresh(feedback)
        return feedback
