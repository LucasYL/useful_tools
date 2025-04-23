from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db import get_db
from models import User, Summary
from auth import get_current_user

# Pydantic模型
class SummaryBase(BaseModel):
    video_id: str
    video_title: str
    summary_text: str
    summary_type: str
    language: str

class SummaryCreate(SummaryBase):
    pass

class SummaryResponse(SummaryBase):
    id: int
    created_at: datetime
    is_favorite: bool
    
    class Config:
        orm_mode = True

# 创建路由器
router = APIRouter(tags=["summaries"])

# 保存摘要
@router.post("/", response_model=SummaryResponse)
def create_user_summary(
    summary_data: SummaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查是否已存在相同视频的摘要
    existing_summary = db.query(Summary).filter(
        Summary.user_id == current_user.id,
        Summary.video_id == summary_data.video_id,
        Summary.summary_type == summary_data.summary_type,
        Summary.language == summary_data.language
    ).first()
    
    # 已存在则更新
    if existing_summary:
        existing_summary.summary_text = summary_data.summary_text
        existing_summary.video_title = summary_data.video_title
        existing_summary.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_summary)
        return existing_summary
    
    # 创建新摘要
    db_summary = Summary(
        user_id=current_user.id,
        video_id=summary_data.video_id,
        video_title=summary_data.video_title,
        summary_text=summary_data.summary_text,
        summary_type=summary_data.summary_type,
        language=summary_data.language
    )
    
    # 保存到数据库
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    
    return db_summary

# 获取用户所有摘要
@router.get("/", response_model=List[SummaryResponse])
def get_user_summaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    favorite_only: bool = False
):
    # 构建查询
    query = db.query(Summary).filter(Summary.user_id == current_user.id)
    
    # 筛选收藏
    if favorite_only:
        query = query.filter(Summary.is_favorite == True)
    
    # 排序并分页
    summaries = query.order_by(Summary.created_at.desc()).offset(skip).limit(limit).all()
    
    return summaries

# 获取单个摘要
@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(
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
    
    return summary

# 更新摘要收藏状态
@router.patch("/{summary_id}/favorite", response_model=SummaryResponse)
def toggle_favorite(
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
    
    # 切换收藏状态
    summary.is_favorite = not summary.is_favorite
    db.commit()
    db.refresh(summary)
    
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