from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.attachment import AttachmentCreateWithoutBlogId, AttachmentOut, AttachmentCreate
from app.crud.attachment import create_attachment, delete_attachment, get_attachments_by_blog
import cloudinary.uploader
from app import models
from app.api import deps

router = APIRouter()

@router.post("/blog/{blog_id}", response_model=AttachmentOut)
def create_attachment_endpoint(
    blog_id: int,
    attachment_in: AttachmentCreateWithoutBlogId,
    db: Session = Depends(get_db)
):
    attachment_data = attachment_in.model_dump()
    attachment_data["blog_id"] = blog_id
    attachment_schema = AttachmentCreate(**attachment_data)
    return create_attachment(db, attachment_schema)

@router.delete("/{attachment_id}")
def delete_attachment_endpoint(
    attachment_id: int,
    db: Session = Depends(deps.get_db)
):

    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    result = cloudinary.uploader.destroy(attachment.file_public_id)
    if result.get("result") != "ok":
        raise HTTPException(status_code=500, detail="Failed to delete from Cloudinary")

    db.delete(attachment)
    db.commit()

    return {"id": attachment_id}

@router.get("/blog/{blog_id}", response_model=List[AttachmentOut])
def get_attachments_endpoint(blog_id: int, db: Session = Depends(get_db)):
    return get_attachments_by_blog(db, blog_id)



