from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.models.blog import Blog, Comment
from app.models.blog_interaction import BlogInteraction
from app.schemas.blog import BlogCreate, BlogOut, BlogUpdate
from app.schemas.interaction import InteractionOut
from app.schemas.comment import CommentCreate, CommentOut, CommentUpdate
from app.schemas.user import BlogAuthorOut
from app.db.session import get_db
from app.core.security import get_current_user
from typing import Optional
from datetime import datetime, timezone
from fastapi import Query
from sqlalchemy import case

router = APIRouter()

from fastapi.responses import JSONResponse
from math import ceil

@router.get("/", response_model=dict)
def get_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None)
):
    skip = (page - 1) * page_size

    total_items = db.query(Blog).count()
    total_pages = ceil(total_items / page_size)

    blogs = (
        db.query(Blog)
        .order_by(Blog.created_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    result = []
    for blog in blogs:
        blog_out = BlogOut.model_validate(blog, from_attributes=True)
        blog_out.author = BlogAuthorOut.model_validate(blog.author, from_attributes=True)

        if current_user:
            interaction = (
                db.query(BlogInteraction)
                .filter_by(blog_id=blog.id, user_id=current_user.id)
                .first()
            )
            if interaction:
                blog_out.interaction = InteractionOut.model_validate(interaction, from_attributes=True)
            else:
                blog_out.interaction = InteractionOut(seen=False, liked=False, unliked=False)

        result.append(blog_out)

    return {
        "data": result,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }


@router.get("/myblogs/", response_model=dict)
def get_my_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    skip = (page - 1) * page_size

    total_items = db.query(Blog).filter(Blog.author_id == current_user.id).count()
    total_pages = ceil(total_items / page_size)

    blogs = (
        db.query(Blog)
        .filter(Blog.author_id == current_user.id)
        .order_by(Blog.created_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    result = []
    for blog in blogs:
        blog_out = BlogOut.model_validate(blog, from_attributes=True)
        blog_out.author = BlogAuthorOut.model_validate(current_user, from_attributes=True)

        interaction = (
            db.query(BlogInteraction)
            .filter_by(blog_id=blog.id, user_id=current_user.id)
            .first()
        )
        if interaction:
            blog_out.interaction = InteractionOut.model_validate(interaction, from_attributes=True)
        else:
            blog_out.interaction = InteractionOut(seen=False, liked=False, unliked=False)

        result.append(blog_out)

    return {
        "data": result,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }





@router.post("/", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
def create_blog(
    blog_in: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):


    new_blog = Blog(
        title=blog_in.title,
        content=blog_in.content,
        image=blog_in.image,
        is_published=blog_in.is_published,
        author_id=current_user.id,
    )

    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return BlogOut.model_validate(new_blog, from_attributes=True)


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog_detail(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) 
):
    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id, Blog.is_published == True)
        .first()
    )

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog_out = BlogOut.model_validate(blog, from_attributes=True)
    blog_out.author = BlogAuthorOut.model_validate(blog.author, from_attributes=True)

    if current_user:
        interaction = (
            db.query(BlogInteraction)
            .filter_by(blog_id=blog.id, user_id=current_user.id)
            .first()
        )
        if interaction:
            blog_out.interaction = InteractionOut.model_validate(interaction, from_attributes=True)
        else:
            blog_out.interaction = InteractionOut(seen=False, liked=False, unliked=False)

    return blog_out



@router.patch("/{blog_id}", response_model=BlogOut)
def update_blog(
    blog_id: int,
    blog_in: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this blog")

    update_data = blog_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(blog, key, value)

    db.commit()
    db.refresh(blog)

    return BlogOut.model_validate(blog, from_attributes=True)


@router.post("/{blog_id}/mark-seen", status_code=200)
def mark_blog_seen(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    interaction = (
        db.query(BlogInteraction)
        .filter_by(blog_id=blog_id, user_id=current_user.id)
        .first()
    )

    if interaction:
        if not interaction.seen:
            interaction.seen = True
            blog.read_count += 1
            interaction.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(blog)
            db.refresh(interaction)
            return {"message": "Marked as seen", "read_count": blog.read_count, "id": blog_id}
        else:
            return {"message": "Already seen", "read_count": blog.read_count, "id": blog_id}

    new_interaction = BlogInteraction(
        blog_id=blog_id,
        user_id=current_user.id,
        seen=True
    )
    blog.read_count += 1
    db.add(new_interaction)

    db.commit()
    db.refresh(blog)
    db.refresh(new_interaction)

    return {"message": "Marked as seen", "read_count": blog.read_count, "id": blog_id}


@router.post("/{blog_id}/like", response_model=BlogOut)
def like_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    interaction = (
        db.query(BlogInteraction)
        .filter_by(blog_id=blog.id, user_id=current_user.id)
        .first()
    )

    if not interaction:
        interaction = BlogInteraction(user_id=current_user.id, blog_id=blog.id, seen=True)
        db.add(interaction)

    if not interaction.liked:
        if interaction.unliked:
            blog.unlikes -= 1

        interaction.liked = True
        interaction.unliked = False
        blog.likes += 1
    else:
        interaction.liked = False
        blog.likes -= 1


    db.commit()
    db.refresh(blog)
    db.refresh(interaction)

    blog_out = BlogOut.model_validate(blog, from_attributes=True)
    blog_out.interaction = InteractionOut.model_validate(interaction, from_attributes=True)
    blog_out.author = blog.author

    return blog_out


@router.post("/{blog_id}/unlike", response_model=BlogOut)
def unlike_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    interaction = (
        db.query(BlogInteraction)
        .filter_by(blog_id=blog.id, user_id=current_user.id)
        .first()
    )

    if not interaction:
        interaction = BlogInteraction(user_id=current_user.id, blog_id=blog.id, seen=True)
        db.add(interaction)

    if not interaction.unliked:
        if interaction.liked:
            blog.likes -= 1

        interaction.unliked = True
        interaction.liked = False
        blog.unlikes += 1
    else:
        interaction.unliked = False
        blog.unlikes -= 1


    db.commit()
    db.refresh(blog)
    db.refresh(interaction)

    blog_out = BlogOut.model_validate(blog, from_attributes=True)
    blog_out.interaction = InteractionOut.model_validate(interaction, from_attributes=True)
    blog_out.author = blog.author

    return blog_out


@router.delete("/{blog_id}", response_model=BlogOut)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this blog")

    db.delete(blog)
    db.commit()

    return BlogOut.model_validate(blog, from_attributes=True)


@router.get("/{blog_id}/comments", response_model=List[CommentOut])
def get_blog_comments(
    blog_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    query = db.query(Comment).filter(Comment.blog_id == blog_id)

    if not current_user.is_superuser:
        query = query.filter(Comment.is_approved == True)


    user_first_case = case(
        (Comment.user_id == current_user.id, 0), 
        else_=1                                   
    )    

    comments = (
        query
        .order_by(user_first_case, Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments



@router.post("/{blog_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(blog_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    comment = Comment(
        content=comment_in.content,
        blog_id=blog_id,
        user_id=current_user.id,
        is_approved=True,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.patch("/comments/{comment_id}/toggle-approval", response_model=CommentOut)
def toggle_comment_approval(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superuser can toggle comment approval")
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.is_approved = not comment.is_approved
    db.commit()
    db.refresh(comment)
    
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    update_data = comment_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(comment, key, value)

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", response_model=CommentOut)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
    return comment