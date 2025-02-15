from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# Tag 모델 정의
class TagBase(BaseModel):
    tagname: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    tid: int

    class Config:
        from_attributes = True

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


# Post 모델 정의
class PostBase(BaseModel):
    title: str
    content: str
    time_stamp: date = Field(default_factory=date.today)
    image: Optional[str] = None

class PostCreate(PostBase):
    uid: Optional[int] = None

class Post(PostBase):
    pid: int
    uid: int
    user: Optional[User] = None

    class Config:
        from_attributes = True
