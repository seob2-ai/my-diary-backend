from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict


# ---------- 공통 ----------
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ---------- Diary (요청용) ----------
class DiaryBase(BaseModel):
    """
    일기 작성 공통 필드 (요청용)
    - date는 문자열(YYYY-MM-DD)로 받되, 없어도 됨
    """

    date: Optional[str] = Field(
        default=None,
        description="일기 날짜 (YYYY-MM-DD, 없으면 오늘)",
    )
    emotion: Optional[str] = ""
    event: Optional[str] = ""
    reason: Optional[str] = ""
    insight: Optional[str] = ""
    tomorrow: Optional[str] = ""


class DiaryCreate(DiaryBase):
    """
    POST /api/diary 에서 사용하는 요청 스키마
    """
    pass


# ---------- Diary (응답용) ----------
class DiaryResponse(BaseModel):
    """
    DB 모델(app.models.DiaryEntry)과 1:1로 맞춘 응답 스키마
    - 필드 이름: snake_case (user_id, created_at 등)
    - 타입: DB 모델과 동일하게 date/datetime 사용
    """

    # SQLAlchemy 모델 인스턴스를 그대로 넣어도 Pydantic이 읽도록 설정
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    date: date
    emotion: str
    event: str
    reason: str
    insight: str
    tomorrow: str

    mode: Optional[str] = None
    mode_label: Optional[str] = None
    mode_description: Optional[str] = None
    coaching: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    analysis_meta: Optional[Dict[str, Any]] = None
