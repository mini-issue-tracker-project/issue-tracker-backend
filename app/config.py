import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://default_user:default_pass@localhost:5432/default_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "placeholder")
