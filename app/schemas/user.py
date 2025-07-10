from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    profile_pic: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_pic: Optional[str] = None
    is_active: Optional[bool] = None
    last_login: Optional[datetime] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool 
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class BlogAuthorOut(BaseModel):
    id: int
    username: str
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True
