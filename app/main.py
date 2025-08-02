from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, blog, attachment
from app.db.base import Base
from app.db.session import engine
from decouple import config
from app.core import cloudinary_config

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

@app.get("/")
def read_root():
    return {"message": "BlogBox backend is running 🚀"}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(blog.router, prefix="/api/v1/blogs", tags=["blogs"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["blogs"])
app.include_router(attachment.router, prefix="/api/v1/attachments", tags=["attachments"])