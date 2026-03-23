import json
from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid, utcnow


class EntityRevision(Base):
    __tablename__ = "entity_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[str] = mapped_column(String(36))
    actor_id: Mapped[str | None] = mapped_column(String(36), default=None)
    action: Mapped[str] = mapped_column(String(30))
    _snapshot: Mapped[str] = mapped_column("snapshot", Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    @property
    def snapshot(self) -> dict:
        return json.loads(self._snapshot)

    @snapshot.setter
    def snapshot(self, value: dict) -> None:
        self._snapshot = json.dumps(value)

    def __repr__(self) -> str:
        return f"<EntityRevision {self.entity_type} {self.entity_id[:8]} {self.action}>"
