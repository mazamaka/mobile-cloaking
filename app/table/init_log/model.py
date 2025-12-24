from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.client.model import Client


class InitLog(SQLModel, table=True):
    __tablename__ = "init_logs"

    id: int | None = Field(default=None, primary_key=True)

    # Client relation
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Optional["Client"] = Relationship()

    # Request data
    request_headers: dict[str, Any] = Field(sa_column=Column(JSONB))
    request_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Response
    response_code: int
    response_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
