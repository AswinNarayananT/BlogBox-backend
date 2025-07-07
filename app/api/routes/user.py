from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.db.session import SessionLocal
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.user.UserOut)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    return crud.user.create_user(db, user)

@router.get("/", response_model=List[schemas.user.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.user.get_users(db, skip=skip, limit=limit)
