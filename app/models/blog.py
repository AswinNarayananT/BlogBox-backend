from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    read_count = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    unlikes = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)

    author = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete-orphan")
    interactions = relationship("BlogInteraction", back_populates="blog", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="blog", cascade="all, delete-orphan")




class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blog_id = Column(Integer, ForeignKey("blogs.id"), nullable=False)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="comments")
    blog = relationship("Blog", back_populates="comments")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    file_public_id = Column(String, nullable=False)  
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    blog = relationship("Blog", back_populates="attachments")