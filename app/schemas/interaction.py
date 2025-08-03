from pydantic import BaseModel
from typing import Optional

class InteractionBase(BaseModel):
    seen: bool = False
    liked: bool = False
    unliked: bool = False

class InteractionCreate(InteractionBase):
    pass

class InteractionOut(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    blog_id: Optional[int] = None
    seen: bool
    liked: bool
    unliked: bool

    model_config = {
        "from_attributes": True
    }
