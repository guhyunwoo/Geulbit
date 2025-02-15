from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
import schema, database, model
import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

gemini_model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI()

database.create_tables()

app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 소설 생성
@app.post("/novels")
def generate_novel(novel: schema.PostBase, db: Session = Depends(get_db)):
    db_novel = model.Post(**novel.dict())  # Pydantic → SQLAlchemy 변환
    db.add(db_novel)
    db.commit()
    db.refresh(db_novel)
    print(db_novel)

# 소설 목록 조회
@app.get("/novels")
def get_novels(db: Session = Depends(get_db)):
    return db.query(model.Post).order_by(desc(model.Post.pid)).all()

# 소설 한 편 조회
@app.get("/novels/{novel_id}")
def get_novel(novel_id: int, db: Session = Depends(get_db)):
    return db.query(model.Post).filter(model.Post.pid == novel_id).scalar()

# ai가 소설 수정
@app.post("/ai")
def ai(request: schema.AIRequest):
    response = gemini_model.generate_content(f'{request.content} {request.prompt}')
    ai_reply = response.text
    print(ai_reply)
    return ai_reply