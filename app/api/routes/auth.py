from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import time
import hashlib

from app.db.session import SessionLocal
from app import crud
from app.schemas.user import UserLogin, UserCreate, UserOut
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, CLOUDINARY_API_SECRET
from app.crud.user import create_user, get_user_by_email
from fastapi import Response

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login")
def login(user_cred: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = crud.user.authenticate_user(db, email=user_cred.email, password=user_cred.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account is inactive. Please contact support.")
    
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=int(refresh_token_expires.total_seconds())
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_pic": user.profile_pic,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    }



@router.get("/generate-signature")
def generate_signature():
    timestamp = int(time.time())
    payload_to_sign = f"timestamp={timestamp}{CLOUDINARY_API_SECRET}"
    signature = hashlib.sha1(payload_to_sign.encode("utf-8")).hexdigest()
    return {"timestamp": timestamp, "signature": signature}



@router.post("/auth/token/refresh/")
def refresh_access_token(request: Request, db: Session = Depends(get_db)):

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive or not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access": new_access_token}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")
    return {"message": "Successfully logged out"}