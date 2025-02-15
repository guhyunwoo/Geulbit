from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# User 모델 정의
class UserBase(BaseModel):
    id: str
    psword: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    uid: int

    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    content: str
    prompt: str

# Post 모델 정의
class PostBase(BaseModel):
    title: str
    content: str
    time_stamp: datetime = Field(default_factory=datetime.now)
    image: Optional[str] = None
    like: int = 0  # 추가된 필드

class PostCreate(PostBase):
    uid: Optional[int] = None

class Post(PostBase):
    pid: int
    uid: int
    user: Optional[User] = None
    tags: List["Tag"] = []

    class Config:
        from_attributes = True


# Tag 모델 정의
class TagBase(BaseModel):
    tagname: str = Field(..., max_length=20)

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    tid: int
    posts: List[Post] = []

    class Config:
        from_attributes = True
