from sqlalchemy.orm import Session
from app.models.blog_interaction import BlogInteraction
from app.schemas.interaction import InteractionCreate

def create_or_update_interaction(db: Session, interaction: InteractionCreate, user_id: int, blog_id: int):
    db_interaction = db.query(BlogInteraction).filter(
        BlogInteraction.user_id == user_id,
        BlogInteraction.blog_id == blog_id
    ).first()

    if db_interaction:
        db_interaction.seen = interaction.seen
        db_interaction.liked = interaction.liked
        db_interaction.unliked = interaction.unliked
        db.commit()
        db.refresh(db_interaction)
    else:
        new_interaction = BlogInteraction(
            **interaction.model_dump(),
            user_id=user_id,
            blog_id=blog_id
        )
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)
        db_interaction = new_interaction

    return db_interaction

def get_user_interaction(db: Session, user_id: int, blog_id: int):
    return db.query(BlogInteraction).filter(
        BlogInteraction.user_id == user_id,
        BlogInteraction.blog_id == blog_id
    ).first()
