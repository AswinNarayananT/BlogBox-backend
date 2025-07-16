from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import time
import hashlib

from app.db.session import SessionLocal
from app import crud
from app.schemas.user import UserLogin, UserCreate, UserSelfUpdate, UserOut,ChangePassword
from app.core.security import create_access_token, create_refresh_token, verify_token, get_current_user, get_password_hash, verify_password 
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, CLOUDINARY_API_SECRET
from app.crud.user import create_user, get_user_by_email
from fastapi import Response
from app.models.user import User

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
        samesite="none",
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



@router.patch("/update-profile", response_model=UserOut)
def update_self(
    user_in: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)

    if "username" in update_data:
        user.username = update_data["username"]
    if "profile_pic" in update_data:
        user.profile_pic = update_data["profile_pic"]

    db.commit()
    db.refresh(user)

    return UserOut.model_validate(user, from_attributes=True)



@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    new_hashed = get_password_hash(password_data.new_password)


    user.hashed_password = new_hashed

    db.commit()
    db.refresh(user)

    return {"detail": "Password updated successfully"}



@router.post("/token/refresh")
def refresh_access_token(request: Request, db: Session = Depends(get_db)):

    refresh_token = request.cookies.get("refresh_token")
    print("refresh",refresh_token)
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