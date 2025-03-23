from typing import Any

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..db import ActiveSession
from ..models.content import Content, ContentIncoming, ContentResponse
from ..security import AuthenticatedUser, User, get_current_user

router = APIRouter()


@router.get("/", response_model=list[ContentResponse])
async def list_contents(*, session: Session = ActiveSession) -> Any:
    contents = session.exec(select(Content)).all()
    return contents


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
    return content


@router.post("/", response_model=ContentResponse, dependencies=[Depends(AuthenticatedUser)])
async def create_content(
    *, session: Session = ActiveSession, content: ContentIncoming, current_user: User = Depends(get_current_user)
) -> Any:
    # Set the ownership of the content to the current user
    new_content = Content.from_orm(content)
    new_content.user_id = current_user.id
    session.add(new_content)
    session.commit()
    session.refresh(new_content)
    return new_content


@router.patch(
    "/{content_id}/",
    response_model=ContentResponse,
    dependencies=[Depends(AuthenticatedUser)],
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

    # Commit the session
    session.add(content)
    session.commit()
    session.refresh(content)
    return content


@router.delete("/{content_id}/", dependencies=[Depends(AuthenticatedUser)])
def delete_content(
    *, session: Session = ActiveSession, content_id: int, current_user: User = Depends(get_current_user)
) -> Any:
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user has permission to delete
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this content")

    session.delete(content)
    session.commit()
    return {"ok": True}
