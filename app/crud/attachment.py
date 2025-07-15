from sqlalchemy.orm import Session
from app.models import Attachment
from app.schemas.attachment import AttachmentCreate

def create_attachment(db: Session, attachment: AttachmentCreate):
    db_attachment = Attachment(**attachment.dict())
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def delete_attachment(db: Session, attachment_id: int):
    db_attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if db_attachment:
        db.delete(db_attachment)
        db.commit()
        return {"message": "Attachment deleted successfully"}
    return {"error": "Attachment not found"}

def get_attachments_by_blog(db: Session, blog_id: int):
    return db.query(Attachment).filter(Attachment.blog_id == blog_id).all()

