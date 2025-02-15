from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends, Body
from sqlalchemy import func
from sqlalchemy.orm import Session
import model, schema, database
from datetime import datetime, timedelta
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
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 저축 로그 불러오기
@app.get("/log")
def get_log_all(db: Session = Depends(get_db)):
    return db.query(model.Log).order_by(model.Log.date.desc()).all()

# 주간 저축 로그
@app.get("/log/weekly")
def get_weekly_amount(db: Session = Depends(get_db)):
    # 현재 날짜와 시간 가져오기
    now = datetime.now()

    # 매주 일요일~토요일까지 모은 돈 계산
    sunday_start = (now - timedelta(days=(now.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
    saturday_end = sunday_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

# 이번 주 일요일부터 토요일까지의 로그만 가져오기
    return (
    db.query(func.sum(model.Log.coin))
    .filter(model.Log.date >= sunday_start, model.Log.date <= saturday_end)  # 일요일부터 토요일까지의 로그
    .scalar() or 0  # 결과 가져오기
    )
# 저축 로그 생성
@app.post("/log")
def create_log(log: schema.LogBase, db: Session = Depends(get_db)):
    max_goal_id = db.query(func.max(model.Goal.goal_id)).scalar() or 0
    db_log = model.Log(coin = log.coin, goal_id=max_goal_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

# 목표 로그 불러오기
@app.get("/goal")
def get_goals(db: Session = Depends(get_db)):
    return db.query(model.Goal).order_by(model.Goal.goal_id.desc()).all()

# 목표 로그 생성
@app.post("/goal")
def create_goal(
    db: Session = Depends(get_db),
    goal_value : int = Body(...),
    goal_name : str = Body(...),
    description : Optional[str] = Body(None)
):
    db_goal = model.Goal(
        goal_value=goal_value,
        goal_name=goal_name,
        description=description
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)