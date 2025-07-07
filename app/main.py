from fastapi import FastAPI
from app.api.routes import user, auth
from app.models import user as user_models
from app.db.base import Base
from app.db.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
