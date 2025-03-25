from datetime import datetime
from typing import Any

from pydantic import BaseModel, Extra
from sqlmodel import Field, SQLModel


class Content(SQLModel):
    """This is an example model for your application.

    Replace with the *things* you do in your application.
    """

    model_config = {"table": True}

    id: int | None = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(default=None)
    text: str
    published: bool = False
    created_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    tags: str = Field(default="")
    user_id: int | None = Field(foreign_key="user.id")

    # Removing relationship for simplicity in testing

    @property
    def tags_list(self) -> list[str]:
        """Property to get the tags as a list."""
        return self.tags.split(",") if self.tags else []


class ContentResponse(BaseModel):
    """This the serializer exposed on the API"""

    id: int
    title: str
    slug: str
    text: str
    published: bool
    created_time: str
    tags: list[str]
    user_id: int

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # tags to model representation
        if kwargs.get("tags") and isinstance(kwargs["tags"], str):
            kwargs["tags"] = kwargs["tags"].split(",") if kwargs["tags"] else []
        super().__init__(*args, **kwargs)


class ContentIncoming(BaseModel):
    """This is the serializer used for POST/PATCH requests"""

    title: str | None
    text: str | None
    published: bool | None = False
    tags: list[str] | str | None
    user_id: int | None = None

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # tags to database representation
        if kwargs.get("tags") and isinstance(kwargs["tags"], list):
            kwargs["tags"] = ",".join(kwargs["tags"])
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self) -> None:
        """Generate a slug from the title."""
        if self.title:
            self.slug = self.title.lower().replace(" ", "-")
