from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func

prefer_tag = Table(
    "prefer_tag",
    Base.metadata,
    Column("pid", Integer, ForeignKey("posts.pid"), primary_key=True),
    Column("tid", Integer, ForeignKey("tags.tid"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(20), nullable=False)
    psword = Column(String(20), nullable=False)
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    pid = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey('users.uid'))
    title = Column(String(20), nullable=False)
    content = Column(String(15000), nullable=False)
    time_stamp = Column(Date, nullable=False, server_default=func.current_date())
    image = Column(String(1000), nullable=True)
    user = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=prefer_tag, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"

    tid = Column(Integer, primary_key=True, autoincrement=True)
    tagname = Column(String(20), nullable=False, unique=True)

    posts = relationship("Post", secondary=prefer_tag, back_populates="tags")