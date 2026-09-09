from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.types import new_id, utcnow


class IndicatorModel(Base):
    __tablename__ = "threat_indicators"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    value: Mapped[str] = mapped_column(String(512), index=True)
    type: Mapped[str] = mapped_column(String(16), index=True)
    source: Mapped[str] = mapped_column(String(128))
    confidence: Mapped[int] = mapped_column(Integer, default=50)
    severity: Mapped[str] = mapped_column(String(16), default="medium")
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    attack: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AttackTechniqueModel(Base):
    __tablename__ = "attack_techniques"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)  # T1110
    name: Mapped[str] = mapped_column(String(255))
    tactic: Mapped[str] = mapped_column(String(32), index=True)
    tactic_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
