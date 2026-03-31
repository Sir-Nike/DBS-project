import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file into environment

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret')

    # MySQL
    DB_HOST     = os.getenv('DB_HOST',     'localhost')
    DB_USER     = os.getenv('DB_USER',     'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME     = os.getenv('DB_NAME',     'quiz_db')
