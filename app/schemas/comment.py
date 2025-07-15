from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOut

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str

class CommentOut(CommentBase):
    id: int
    user_id: int
    blog_id: int
    is_approved: bool
    created_at: datetime
    user: UserOut

    class Config:
        orm_mode = True
