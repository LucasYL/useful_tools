from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db import get_db
from models import User, Summary, Video
from auth import get_current_user

# Pydantic模型
class SummaryBase(BaseModel):
    summary_text: str
    transcript_text: Optional[str] = None

class SummaryCreate(SummaryBase):
    video_id: int  # 关联到视频表的ID
    summary_type: Optional[str] = "short"
    language: Optional[str] = "en"

class SummaryResponse(SummaryBase):
    id: int
    user_id: int
    video_id: int
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 包含视频信息的扩展响应模型
class SummaryWithVideoResponse(SummaryResponse):
    video_title: str
    video_youtube_id: str
    video_thumbnail_url: Optional[str] = None
    summary_type: str
    language: str
    
    class Config:
        from_attributes = True

# 收藏状态更新模型
class FavoriteUpdate(BaseModel):
    is_favorite: bool

# 创建路由器
router = APIRouter(tags=["summaries"])

# 保存摘要
@router.post("/", response_model=SummaryResponse)
def create_user_summary(
    summary_data: SummaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查视频是否存在
    video = db.query(Video).filter(Video.id == summary_data.video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # 检查是否已存在该用户对此视频的摘要
    existing_summary = db.query(Summary).filter(
        Summary.user_id == current_user.id,
        Summary.video_id == summary_data.video_id
    ).first()
    
    # 已存在则更新
    if existing_summary:
        existing_summary.summary_text = summary_data.summary_text
        if summary_data.transcript_text:
            existing_summary.transcript_text = summary_data.transcript_text
        db.commit()
        db.refresh(existing_summary)
        return existing_summary
    
    # 创建新摘要
    db_summary = Summary(
        user_id=current_user.id,
        video_id=summary_data.video_id,
        summary_text=summary_data.summary_text,
        transcript_text=summary_data.transcript_text,
        summary_type=summary_data.summary_type,
        language=summary_data.language
    )
    
    # 保存到数据库
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    
    return db_summary

# 获取用户所有摘要
@router.get("/", response_model=List[SummaryWithVideoResponse])
def get_user_summaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    # 构建查询
    summaries = db.query(
        Summary.id,
        Summary.user_id,
        Summary.video_id,
        Summary.summary_text,
        Summary.transcript_text,
        Summary.is_favorite,
        Summary.summary_type,
        Summary.language,
        Summary.created_at,
        Video.title.label("video_title"),
        Video.youtube_id.label("video_youtube_id"),
        Video.thumbnail_url.label("video_thumbnail_url")
    ).join(Video, Summary.video_id == Video.id)\
    .filter(Summary.user_id == current_user.id)\
    .order_by(Summary.created_at.desc())\
    .offset(skip).limit(limit).all()
    
    return summaries

# 获取单个摘要
@router.get("/{summary_id}", response_model=SummaryWithVideoResponse)
def get_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询摘要，确保是当前用户的，并包含视频信息
    summary = db.query(
        Summary.id,
        Summary.user_id,
        Summary.video_id,
        Summary.summary_text,
        Summary.transcript_text,
        Summary.is_favorite,
        Summary.summary_type,
        Summary.language,
        Summary.created_at,
        Video.title.label("video_title"),
        Video.youtube_id.label("video_youtube_id"),
        Video.thumbnail_url.label("video_thumbnail_url")
    ).join(Video, Summary.video_id == Video.id)\
    .filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    # 检查是否存在
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return summary

# 删除摘要
@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询摘要，确保是当前用户的
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    # 检查是否存在
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    # 删除摘要
    db.delete(summary)
    db.commit()

# 更新收藏状态
@router.put("/{summary_id}/favorite", response_model=SummaryResponse)
def toggle_favorite(
    summary_id: int,
    favorite_data: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询摘要，确保是当前用户的
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == current_user.id
    ).first()
    
    # 检查是否存在
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    # 更新收藏状态
    summary.is_favorite = favorite_data.is_favorite
    db.commit()
    db.refresh(summary)
    
    return summary 