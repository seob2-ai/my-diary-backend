# app/routers/analytics.py
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional, Dict, List

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user_id
from ..constants import StreakConstants
from ..utils import parse_date_range, handle_api_error, create_empty_emotion_response, create_empty_streak_response
from ..services.emotion_service import (
    calculate_emotion_score,
    categorize_emotion,
    get_emotion_label_ko,
    calculate_trend,
    generate_emotion_insights,
    aggregate_emotion_data,
    aggregate_by_granularity
)
from ..services.streak_service import (
    calculate_streak,
    get_calendar_data,
    calculate_weekly_progress,
    calculate_achievement_badges,
    get_streak_insights
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analytics"])


@router.get(
    "/analytics/emotion-trends",
    response_model=schemas.EmotionTrendsResponse,
)
def get_emotion_trends(
    start_date: Optional[str] = Query(
        default=None,
        alias="start_date",
        description="시작 날짜 (YYYY-MM-DD, 기본값: 30일 전)"
    ),
    end_date: Optional[str] = Query(
        default=None,
        alias="end_date",
        description="종료 날짜 (YYYY-MM-DD, 기본값: 오늘)"
    ),
    granularity: str = Query(
        default="day",
        regex="^(day|week|month)$",
        description="집계 단위 (day|week|month)"
    ),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    감정 트렌드 분석
    
    - 감정 필드를 분석하여 일별/주별/월별 감정 변화 추적
    - 감정 점수(-1.0 ~ 1.0), 분포, 트렌드 인사이트 제공
    """
    try:
        # 날짜 범위 계산
        start, end = parse_date_range(start_date, end_date, default_days=30)
        
        logger.info(f"감정 트렌드 분석 요청: user_id={user_id}, start={start}, end={end}, granularity={granularity}")
        
        # 해당 기간의 일기 조회
        entries = (
            db.query(models.DiaryEntry)
            .filter(
                models.DiaryEntry.user_id == user_id,
                models.DiaryEntry.date >= start,
                models.DiaryEntry.date <= end,
            )
            .order_by(models.DiaryEntry.date.asc())
            .all()
        )
        
        if not entries:
            return create_empty_emotion_response(start, end, granularity)
        
        # 일별 감정 데이터 집계
        daily_data, all_scores, emotion_distribution = aggregate_emotion_data(entries)
        
        # granularity에 따라 집계 단위 결정
        trends_data = aggregate_by_granularity(
            daily_data, entries, start, end, granularity
        )
        
        # DailyEmotionTrend 스키마로 변환
        daily_trends = [
            schemas.DailyEmotionTrend(**trend) for trend in trends_data
        ]
        
        # 평균 점수 계산
        average_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # 트렌드 계산 (이전 기간과 비교)
        period_days = (end - start).days + 1
        previous_start = start - timedelta(days=period_days)
        
        previous_entries = (
            db.query(models.DiaryEntry)
            .filter(
                models.DiaryEntry.user_id == user_id,
                models.DiaryEntry.date >= previous_start,
                models.DiaryEntry.date < start,
            )
            .all()
        )
        
        previous_scores = [
            calculate_emotion_score(e.emotion)[0]
            for e in previous_entries
            if e.emotion
        ]
        
        trend = calculate_trend(all_scores, previous_scores)
        
        # 인사이트 생성
        daily_trends_dict = [
            {
                "date": trend.entry_date.isoformat(),
                "emotion_score": trend.emotion_score,
                "entry_count": trend.entry_count
            }
            for trend in daily_trends
        ]
        
        insights = generate_emotion_insights(
            daily_trends_dict,
            dict(emotion_distribution),
            period_days
        )
        
        logger.info(f"감정 트렌드 분석 완료: total_entries={len(entries)}, avg_score={average_score:.2f}, trend={trend}")
        
        return schemas.EmotionTrendsResponse(
            period={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "granularity": granularity,
                "days": period_days
            },
            emotion_distribution=dict(emotion_distribution),
            daily_trends=daily_trends,
            insights=insights,
            average_score=round(average_score, 2),
            trend=trend
        )
        
    except HTTPException:
        raise
    except Exception as e:
        handle_api_error("감정 트렌드 분석", e, logger, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/analytics/streak",
    response_model=schemas.StreakResponse,
)
def get_streak(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    weekly_goal: Optional[int] = Query(
        default=StreakConstants.DEFAULT_WEEKLY_GOAL,
        ge=StreakConstants.MIN_WEEKLY_GOAL,
        le=7,
        description="주간 목표 작성 수 (1-7일)"
    ),
):
    """
    일기 작성 연속성(Streak) 추적
    
    - 현재 연속 작성 일수
    - 최장 연속 기록
    - 총 작성 일수
    - 캘린더 히트맵 데이터
    - 주간 목표 및 진행도
    - 달성 배지
    """
    try:
        today = date.today()
        logger.info(f"Streak 조회 요청: user_id={user_id}")
        
        # 사용자의 모든 일기 조회
        entries = (
            db.query(models.DiaryEntry)
            .filter(models.DiaryEntry.user_id == user_id)
            .order_by(models.DiaryEntry.date.asc())
            .all()
        )
        
        if not entries:
            return create_empty_streak_response(weekly_goal)
        
        # 날짜 리스트 추출
        dates = [entry.date for entry in entries]
        
        # 연속 기록 계산
        current_streak, longest_streak = calculate_streak(dates, today)
        
        # 총 작성 일수 (중복 제거)
        total_days = len(set(dates))
        
        # 캘린더 데이터 생성 (최근 90일 또는 첫 작성일부터)
        oldest_date = min(dates)
        start_date = min(oldest_date, today - timedelta(days=90))
        calendar_data = get_calendar_data(dates, start_date, today)
        
        # 주간 진행도 계산
        weekly_progress = calculate_weekly_progress(dates, today)
        
        # 배지 계산
        badges = calculate_achievement_badges(total_days, longest_streak, current_streak)
        
        logger.info(
            f"Streak 계산 완료: current={current_streak}, longest={longest_streak}, "
            f"total={total_days}, weekly={weekly_progress}/{weekly_goal}"
        )
        
        return schemas.StreakResponse(
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_days=total_days,
            calendar_data=calendar_data,
            weekly_goal=weekly_goal,
            weekly_progress=weekly_progress,
            achievement_badges=badges,
            streak_freeze_used=False  # 나중에 기능 추가 시 구현
        )
        
    except HTTPException:
        raise
    except Exception as e:
        handle_api_error("Streak 조회", e, logger, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

