from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.orm import Session
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

# @app.post("/novels")
# def generate_novel(novel: schema.PostBase, db: Session = Depends(get_db)):
#     db.add(novel)
#     db.commit()
#     db.refresh(novel)
#     print(novel)

@app.get("/novels")
def get_novels(db: Session = Depends(get_db)):
    return db.query(model.Post).order_by(model.Post.pid).all()