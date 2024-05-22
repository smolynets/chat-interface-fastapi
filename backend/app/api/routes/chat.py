from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    ChatMessage,
    ChatMessageCreate,
    ChatMessagesPublic,
    ChatMessagePublic,
    ChatMessageUpdate
)
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/", response_model=ChatMessagesPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = None, limit: int = None
) -> Any:
    """
    Retrieve chat_messages.
    """

    if limit is None:
        limit = 2

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(ChatMessage)
        count = session.exec(count_statement).one()
        statement = select(ChatMessage).order_by(ChatMessage.id).offset(skip).limit(limit)
        chat_messages = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(ChatMessage)
            .where(ChatMessage.owner_id == current_user.id)
            .order_by(ChatMessage.id)
            .offset(skip)
            .limit(limit)
        )
        chat_messages = session.exec(statement).all()

    return ChatMessagesPublic(data=chat_messages, count=count)


@router.get("/{id}", response_model=ChatMessagePublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get ChatMessage by ID.
    """
    chat_message = session.get(ChatMessage, id)
    if not chat_message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (chat_message.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return chat_message


@router.post("/", response_model=ChatMessagePublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, message_in: ChatMessageCreate
) -> Any:
    """
    Create new chat_message.
    """
    chat_message = ChatMessage.model_validate(message_in, update={"owner_id": current_user.id})
    session.add(chat_message)
    session.commit()
    session.refresh(chat_message)
    return chat_message


@router.put("/{id}", response_model=ChatMessagePublic)
def update_item(
    *, session: SessionDep, current_user: CurrentUser, id: int, chat_message_in: ChatMessageUpdate
) -> Any:
    """
    Update an ChatMessage.
    """
    thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
    chat_message = session.get(ChatMessage, id)
    if not chat_message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (ChatMessage.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if chat_message.created_at < thirty_minutes_ago:
        raise HTTPException(status_code=400, detail="Message created more than 30 min ago!")
    update_dict = chat_message_in.model_dump(exclude_unset=True)
    chat_message.sqlmodel_update(update_dict)
    session.add(chat_message)
    session.commit()
    session.refresh(chat_message)
    return chat_message


@router.delete("/{id}")
def delete_item(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an ChatMessage.
    """
    chat_message = session.get(ChatMessage, id)
    if not chat_message:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(chat_message)
    session.commit()
    return Message(message="ChatMessage deleted successfully")
