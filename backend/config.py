import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS settings for frontend
    CORS_HEADERS = 'Content-Type'