from datetime import datetime

from sqlmodel import Field


def created_at_field() -> datetime:
    return Field(default_factory=datetime.utcnow)


def updated_at_field() -> datetime:
    return Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
