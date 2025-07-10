from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import user, auth, blog
from app.db.base import Base
from app.db.session import engine
from decouple import config

Base.metadata.create_all(bind=engine)

app = FastAPI()

frontend_url = config("FRONTEND_URL", default="http://localhost:5173")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(blog.router, prefix="/api/v1/blogs", tags=["blogs"])
