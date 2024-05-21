from sqlmodel import Field, Relationship, SQLModel, Column, DateTime
from typing import Optional
from datetime import datetime


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    messages: list["ChatMessage"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


class ChatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="messages")
    created_at: Optional[datetime] = Column(DateTime, default=datetime.now(), nullable=True)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ChatMessageCreate(SQLModel):
    title: str
    text: str


class ChatMessagePublic(SQLModel):
    id: int
    title: str
    text: str
    owner_id: int


class ChatMessagesPublic(SQLModel):
    data: list[ChatMessagePublic]
    count: int


class ChatMessageUpdate(SQLModel):
    title: str
    text: str
