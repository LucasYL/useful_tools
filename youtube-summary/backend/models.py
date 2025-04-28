from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 一对多关系定义
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")

class Video(Base):
    """视频表"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    youtube_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    channel = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # 一对多关系定义
    summaries = relationship("Summary", back_populates="video", cascade="all, delete-orphan")
    # 多对多关系定义
    tags = relationship("Tag", secondary="video_tags", back_populates="videos")

class Summary(Base):
    """摘要表"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary_text = Column(Text, nullable=False)
    transcript_text = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False, nullable=False)
    summary_type = Column(String, default="short", nullable=False)
    language = Column(String, default="en", nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # 多对一关系定义
    user = relationship("User", back_populates="summaries")
    video = relationship("Video", back_populates="summaries")

class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    # 多对多关系定义
    videos = relationship("Video", secondary="video_tags", back_populates="tags")

# 视频-标签关联表
class VideoTag(Base):
    """视频-标签关联表"""
    __tablename__ = "video_tags"
    
    video_id = Column(Integer, ForeignKey("videos.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True) 