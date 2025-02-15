from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .model import Log, Goal
from .base import Base

load_dotenv()
user = os.getenv("DB_USER")
host = os.getenv("DB_HOST")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:3306/{database}?charset=utf8"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 객체를 상속받은 모든 테이블 생성
def create_tables():
    Base.metadata.create_all(engine)