from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.types import new_id, utcnow


class NormalizedEventModel(Base):
    __tablename__ = "normalized_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    raw_event_id: Mapped[str] = mapped_column(String(36), index=True)
    environment_id: Mapped[str] = mapped_column(String(36), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=utcnow)
    source_type: Mapped[str] = mapped_column(String(48), index=True)

    event_action: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    event_outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)
    event_category: Mapped[str | None] = mapped_column(String(48), nullable=True, index=True)

    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(16), nullable=True)

    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    host_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    process_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    bytes_out: Mapped[int | None] = mapped_column(Integer, nullable=True)

    message: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)
