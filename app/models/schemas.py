from typing import Literal

from pydantic import BaseModel, Field


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[Turn] = Field(default_factory=list, max_length=10)


class FeedbackRequest(BaseModel):
    message_id: int
    value: Literal[1, -1]


class HireRequest(BaseModel):
    role_type: str = Field(min_length=2, max_length=100)
    scope: str = Field(min_length=5, max_length=1500)
    skills: list[str] = Field(default_factory=list, max_length=15)
    name: str = Field(default="", max_length=100)
    email: str = Field(default="", max_length=200)
