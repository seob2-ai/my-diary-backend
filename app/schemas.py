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
    - content 필드도 지원 (클라이언트 호환성)
    """

    date: Optional[str] = Field(
        default=None,
        description="일기 날짜 (YYYY-MM-DD, 없으면 오늘)",
    )
    # 클라이언트 호환성: content 필드 지원
    content: Optional[str] = Field(
        default=None,
        description="일기 내용 (단일 필드 형식, emotion/event 등으로 분리됨)",
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


class DiaryUpdate(BaseModel):
    """
    PUT/PATCH /api/diary/{diary_id} 에서 사용하는 요청 스키마
    모든 필드가 선택적 (부분 업데이트 지원)
    """
    date: Optional[str] = Field(
        default=None,
        description="일기 날짜 (YYYY-MM-DD)",
    )
    content: Optional[str] = Field(
        default=None,
        description="일기 내용 (단일 필드 형식)",
    )
    emotion: Optional[str] = None
    event: Optional[str] = None
    reason: Optional[str] = None
    insight: Optional[str] = None
    tomorrow: Optional[str] = None


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
    emotion: Optional[str] = None
    event: Optional[str] = None
    reason: Optional[str] = None
    insight: Optional[str] = None
    tomorrow: Optional[str] = None

    mode: Optional[str] = None
    mode_label: Optional[str] = None
    mode_description: Optional[str] = None
    coaching: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    analysis_meta: Optional[Dict[str, Any]] = None

# ---------- Diary 분석 결과 (저장 없이 미리보기용) ----------
class DiaryAnalysisResult(BaseModel):
    mode: Optional[str] = None
    mode_label: Optional[str] = None
    mode_description: Optional[str] = None
    coaching: Optional[str] = None

    # 모호성 정보
    is_ambiguous: bool
    ambiguity_score: float  # 0.0 ~ 1.0 (높을수록 모호)
    ambiguity_reasons: List[str] = []

    analysis_meta: Optional[Dict[str, Any]] = None


# ---------- 통계 응답 ----------
class DiaryStatsResponse(BaseModel):
    """일기 통계 정보"""
    total_count: int = Field(description="전체 일기 개수")
    this_month_count: int = Field(description="이번 달 일기 개수")
    this_week_count: int = Field(description="이번 주 일기 개수")
    mode_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="모드별 일기 개수 분포"
    )
    earliest_date: Optional[date] = Field(
        default=None,
        description="가장 오래된 일기 날짜"
    )
    latest_date: Optional[date] = Field(
        default=None,
        description="가장 최근 일기 날짜"
    )


# ---------- Summary (요약 응답) ----------
class WeeklySummaryResponse(BaseModel):
    """
    주간 요약 응답 스키마
    - startDate: 주간 시작 날짜 (월요일)
    - endDate: 주간 종료 날짜 (일요일)
    - totalEntries: 해당 주간 일기 개수
    - modeCounts: 모드별 일기 개수 분포
    - highlights: 주간 하이라이트 정보
    """
    startDate: date = Field(description="주간 시작 날짜 (월요일)")
    endDate: date = Field(description="주간 종료 날짜 (일요일)")
    totalEntries: int = Field(description="해당 주간 일기 개수")
    modeCounts: Dict[str, int] = Field(
        default_factory=dict,
        description="모드별 일기 개수 분포"
    )
    highlights: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="주간 하이라이트 (가장 긴/짧은 일기 ID, 가장 긍정적인 모드)"
    )

