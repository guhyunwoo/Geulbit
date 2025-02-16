from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from base import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(20), nullable=False, unique=True)
    psword = Column(String(20), nullable=False)
    posts = relationship("Post", back_populates="user")
    likes = relationship("Like", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    pid = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey('users.uid'))
    title = Column(String(20), nullable=True)
    content = Column(String(15000), nullable=False)
    time_stamp = Column(Date, nullable=True, server_default=func.current_date())
    image = Column(String(1000), nullable=True)
    like = Column(Integer, nullable=False, default=0)
    user = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    liked_by = relationship("Like", back_populates="post")

class PostTag(Base):
    __tablename__ = "post_tags"

    pid = Column(Integer, ForeignKey('posts.pid'), primary_key=True)
    tid = Column(Integer, ForeignKey('tags.tid'), primary_key=True)

class Tag(Base):
    __tablename__ = "tags"

    tid = Column(Integer, primary_key=True, autoincrement=True)
    tagname = Column(String(20), nullable=False)
    posts = relationship("Post", secondary="post_tags", back_populates="tags")

class Like(Base):
    __tablename__ = "likes"

    uid = Column(Integer, ForeignKey('users.uid'), primary_key=True)
    pid = Column(Integer, ForeignKey('posts.pid'), primary_key=True)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="liked_by")
