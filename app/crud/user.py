from sqlalchemy.orm import Session
from app import models, schemas
from app.core.security import get_password_hash, verify_password

def create_user(db: Session, user: schemas.user.UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = models.user.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        profile_pic=user.profile_pic
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.user.User).filter(models.user.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.user.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: schemas.user.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user
