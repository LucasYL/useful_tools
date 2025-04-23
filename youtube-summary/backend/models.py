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
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # 一对多关系定义
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")

class Summary(Base):
    """摘要历史表"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(String, nullable=False)
    video_title = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String, nullable=False)
    language = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_favorite = Column(Boolean, default=False)
    
    # 多对一关系定义
    user = relationship("User", back_populates="summaries") 