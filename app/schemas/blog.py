from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.interaction import InteractionOut
from app.schemas.user import BlogAuthorOut
from typing import Optional

class BlogBase(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    attachment: Optional[str] = None
    is_published: Optional[bool] = True

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BlogBase):
    title: Optional[str] = None
    content: Optional[str] = None

class BlogOut(BlogBase):
    id: int
    author_id: int
    read_count: int
    likes: int
    unlikes: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    author: BlogAuthorOut
    interaction: Optional[InteractionOut] = None

    model_config = {"from_attributes": True}


