from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import SessionLocal
from app import crud, schemas
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(user_cred: schemas.user.UserLogin, db: Session = Depends(get_db)):
    user = crud.user.authenticate_user(db, email=user_cred.email, password=user_cred.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
