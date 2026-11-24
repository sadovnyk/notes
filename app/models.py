from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=10_000)


class NoteReplace(BaseModel):
    """Для PUT: повна заміна, обидва поля обов'язкові."""

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(max_length=10_000)


class NoteUpdate(BaseModel):
    """Для PATCH: часткове оновлення, передаються лише поля, які змінюються."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=10_000)


class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str