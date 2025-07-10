from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogUpdate
from typing import List, Optional

def create_blog(db: Session, blog: BlogCreate, user_id: int):
    db_blog = Blog(**blog.model_dump(), author_id=user_id)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

def get_blog(db: Session, blog_id: int) -> Optional[Blog]:
    return db.query(Blog).filter(Blog.id == blog_id, Blog.is_published == True).first()

def get_all_blogs(
    db: Session, skip: int = 0, limit: int = 10, search: Optional[str] = None
) -> List[Blog]:
    query = db.query(Blog).filter(Blog.is_published == True)
    if search:
        query = query.filter(Blog.title.ilike(f"%{search}%"))
    return query.order_by(desc(Blog.created_at)).offset(skip).limit(limit).all()

def update_blog(db: Session, blog_id: int, blog_update: BlogUpdate, user_id: int) -> Optional[Blog]:
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == user_id).first()
    if not blog:
        return None

    update_data = blog_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(blog, key, value)

    db.commit()
    db.refresh(blog)
    return blog

def delete_blog(db: Session, blog_id: int, user_id: int) -> bool:
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == user_id).first()
    if not blog:
        return False

    db.delete(blog)
    db.commit()
    return True

def get_blogs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Blog]:
    return db.query(Blog).filter(Blog.author_id == user_id).order_by(desc(Blog.created_at)).offset(skip).limit(limit).all()
