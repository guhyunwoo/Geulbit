from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.params import Depends
from sqlalchemy.orm import Session
import Jtoken
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

def get_current_user(token: str = Depends(Jtoken.get_current_user)):
    return token.verify_access_token(token)

# 소설 생성
@app.post("/novels", dependencies=[Depends(get_current_user)])
def generate_novel(novel: schema.PostCreate, db: Session = Depends(get_db)):
    db_novel = model.Post(**novel.dict())  # Pydantic → SQLAlchemy 변환
    db.add(db_novel)
    db.commit()
    db.refresh(db_novel)

# 소설 목록 조회
@app.get("/novels")
def get_novels(db: Session = Depends(get_db), user: model.User = Depends(get_current_user)):
    return db.query(model.Post).order_by(desc(model.Post.pid)).all()

# 찜 목록 정렬
@app.get("/novels/like")
def get_novels_like(db: Session = Depends(get_db), user: model.User = Depends(get_current_user)):
    return db.query(model.Post).order_by(desc(model.Post.like)).all()

# 소설 한 편 조회
@app.get("/novels/{novel_id}")
def get_novel(novel_id: int, db: Session = Depends(get_db), user: model.User = Depends(get_current_user)):
    return db.query(model.Post).filter(model.Post.pid == novel_id).scalar()

# ai가 소설 수정
@app.post("/ai")
def ai(request: schema.AIRequest, user: model.User = Depends(get_current_user)):
    response = gemini_model.generate_content(f'{request.content} {request.prompt}')
    ai_reply = response.text
    print(ai_reply)
    return ai_reply

# 태그 생성
@app.post("/tags")
def create_tag(tag: schema.TagBase, db: Session = Depends(get_db), user: model.User = Depends(get_current_user)):
    db_tag = model.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

# 유저 생성 (인증 필요 없음)
@app.post("/users")
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = model.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

# 유저 로그인
@app.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(model.User).filter(model.User.id == form_data.username).first()
    if not user or user.psword != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )

    # JWT 토큰 발급
    access_token = Jtoken.create_access_token(data={"sub": str(user.uid)})
    return {"access_token": access_token, "token_type": "bearer"}

#찜하기
@app.post("/novels/like", dependencies=[Depends(get_current_user)])
def like_novel(req:schema.Like, db: Session = Depends(get_db)):
    novel = db.query(model.Post).filter_by(pid=req.pid).first()
    like_entry = db.query(model.Like).filter_by(uid=req.uid, pid=req.pid).first()

    if like_entry:
        db.delete(like_entry)
        if novel.like > 0:
            novel.like -= 1
    else:
        db.add(model.Like(uid=req.uid, pid=req.pid))
        novel.like += 1

    db.commit()


# 찜한 소설 조회
@app.get("/novels/like/{user_id}")
def get_user_like(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(model.Post)
        .join(model.Like, model.Like.pid == model.Post.pid)
        .filter(model.Like.uid == user_id)
        .all()
    )
