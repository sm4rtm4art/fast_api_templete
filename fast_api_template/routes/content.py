from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..auth_core import User, get_current_active_user, get_current_user
from ..db import ActiveSession
from ..models.content import Content, ContentIncoming, ContentResponse

router = APIRouter()


@router.get("/", response_model=list[ContentResponse])
async def list_contents(*, session: Session = ActiveSession) -> Any:
    contents = session.exec(select(Content)).all()
    return [ContentResponse.model_validate(content) for content in contents]


@router.get("/{id_or_slug}/", response_model=ContentResponse)
async def query_content(*, id_or_slug: str | int, session: Session = ActiveSession) -> Any:
    query = None
    if isinstance(id_or_slug, int):
        query = select(Content).where(Content.id == id_or_slug)
    else:
        query = select(Content).where(Content.slug == id_or_slug)

    content = session.exec(query).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return ContentResponse.model_validate(content)


@router.post(
    "/",
    response_model=ContentResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def create_content(
    *, session: Session = ActiveSession, content: ContentIncoming, current_user: User = Depends(get_current_user)
) -> Any:
    # Set the ownership of the content to the current user
    new_content = Content.model_validate(content)
    new_content.user_id = current_user.id

    # Save to DB
    session.add(new_content)
    session.commit()
    session.refresh(new_content)

    return ContentResponse.model_validate(new_content)


@router.patch(
    "/{content_id}/",
    response_model=ContentResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def update_content(
    *,
    content_id: int,
    session: Session = ActiveSession,
    patch: ContentIncoming,
    current_user: User = Depends(get_current_user),
) -> Any:
    # Query the content
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user has permission to edit
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to edit this content")

    # Update the content
    content_data = patch.dict(exclude_unset=True)
    for key, value in content_data.items():
        setattr(content, key, value)

    session.add(content)
    session.commit()
    session.refresh(content)

    return ContentResponse.model_validate(content)


@router.delete(
    "/{content_id}/",
    dependencies=[Depends(get_current_active_user)],
)
def delete_content(
    *, session: Session = ActiveSession, content_id: int, current_user: User = Depends(get_current_user)
) -> Any:
    # Query the content
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user has permission to delete
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this content")

    # Delete the content
    session.delete(content)
    session.commit()
    return {"status": "success", "message": f"Content {content_id} deleted"}
