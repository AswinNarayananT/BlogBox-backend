from decouple import config

DATABASE_URL = config("DATABASE_URL", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
