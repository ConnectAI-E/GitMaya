from typing import Optional

from pydantic import BaseModel


class Installation(BaseModel):
    id: int


class Sender(BaseModel):
    type: str
    login: str  # name
    id: int


class Organization(BaseModel):
    login: str
    id: int


class BaseEvent(BaseModel):
    organization: Optional[Organization] = None
    sender: Sender
    installation: Optional[Installation] = None


class Repository(BaseModel):
    id: int


class RepoEvent(BaseEvent):
    action: str
    repository: Repository
