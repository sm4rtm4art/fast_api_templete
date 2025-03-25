from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth_core import User, get_current_user
from ..db import get_session
from ..models.content import Content, ContentIncoming, ContentResponse

router = APIRouter()


@router.get("/", response_model=List[ContentResponse])
async def get_contents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Get all contents."""
    contents = session.exec(select(Content).offset(skip).limit(limit)).all()
    return contents


@router.get("/{id_or_slug}/", response_model=ContentResponse)
async def query_content(*, id_or_slug: str | int, session: Session = Depends(get_session)) -> Any:
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
    dependencies=[Depends(get_current_user)],
)
async def create_content(
    content_in: ContentIncoming,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Create a new content."""
    content = Content(
        **content_in.model_dump(),
        user_id=current_user.id,
    )
    session.add(content)
    session.commit()
    session.refresh(content)
    return ContentResponse.model_validate(content)


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_in: ContentIncoming,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    """Update a content."""
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )
    if content.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    for key, value in content_in.model_dump().items():
        setattr(content, key, value)
    session.commit()
    session.refresh(content)
    return ContentResponse.model_validate(content)


@router.delete(
    "/{content_id}/",
    dependencies=[Depends(get_current_user)],
)
def delete_content(
    *, session: Session = Depends(get_session), content_id: int, current_user: User = Depends(get_current_user)
) -> Any:
    # Query the content
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user has permission to delete
    if content.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this content")

    # Delete the content
    session.delete(content)
    session.commit()
    return {"status": "success", "message": f"Content {content_id} deleted"}
