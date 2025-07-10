from sqlalchemy.orm import Session
from app.models.blog import Comment
from app.schemas.comment import CommentCreate

def create_comment(db: Session, comment: CommentCreate, user_id: int, blog_id: int):
    db_comment = Comment(**comment.model_dump(), user_id=user_id, blog_id=blog_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_blog(db: Session, blog_id: int, skip: int = 0, limit: int = 10):
    return db.query(Comment).filter(Comment.blog_id == blog_id).offset(skip).limit(limit).all()

def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment

def approve_comment(db: Session, comment_id: int, is_approved: bool = True):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.is_approved = is_approved
        db.commit()
        db.refresh(comment)
    return comment
