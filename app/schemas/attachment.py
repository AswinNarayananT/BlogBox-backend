from pydantic import BaseModel

class AttachmentCreate(BaseModel):
    file_url: str
    file_public_id: str
    blog_id: int

class AttachmentCreateWithoutBlogId(BaseModel):
    file_url: str
    file_public_id: str

class AttachmentOut(BaseModel):
    id: int
    file_url: str
    file_public_id: str
    blog_id: int

    class Config:
        orm_mode = True
