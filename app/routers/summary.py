# app/routers/summary.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional, Dict, List
from calendar import monthrange

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user_id
from ..constants import get_most_positive_mode
from ..utils import find_longest_shortest_entries, calculate_diary_length, handle_api_error

logger = logging.getLogger(__name__)
router = APIRouter(tags=["summary"])


@router.get(
    "/summary/weekly",
    response_model=schemas.WeeklySummaryResponse,
)
def get_weekly_summary(
    startDate: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    주간 요약 조회
    - startDate가 없으면 현재 주 기준 (월요일 시작)
    """
    try:
        if not startDate:
            today = date.today()
            monday = today - timedelta(days=today.weekday())
            startDate = monday

        endDate = startDate + timedelta(days=6)

        logger.info(f"주간 요약 조회: user_id={user_id}, startDate={startDate}, endDate={endDate}")

        entries = (
            db.query(models.DiaryEntry)
            .filter(
                models.DiaryEntry.user_id == user_id,
                models.DiaryEntry.date >= startDate,
                models.DiaryEntry.date <= endDate,
            )
            .all()
        )

        # 모드별 분포 계산
        mode_counts: Dict[str, int] = {}
        for e in entries:
            if e.mode:
                mode_counts[e.mode] = mode_counts.get(e.mode, 0) + 1

        # 가장 긴/짧은 일기 찾기
        longest_id, shortest_id = find_longest_shortest_entries(entries)
        
        # 가장 긍정적인 모드 찾기
        most_positive_mode = get_most_positive_mode(mode_counts)

        logger.info(f"주간 요약 완료: total={len(entries)}")

        return schemas.WeeklySummaryResponse(
            startDate=startDate,
            endDate=endDate,
            totalEntries=len(entries),
            modeCounts=mode_counts,
            highlights={
                "longestEntryId": longest_id,
                "shortestEntryId": shortest_id,
                "mostPositiveMode": most_positive_mode,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        handle_api_error("주간 요약 조회", e, logger, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/summary/monthly",
    response_model=schemas.MonthlySummaryResponse,
)
def get_monthly_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    월간 요약 조회
    - year, month가 없으면 현재 월 기준
    - 해당 월의 일기 통계, 모드 분포, 하이라이트 제공
    """
    try:
        # 날짜 계산
        today = date.today()
        if not year or not month:
            year = today.year
            month = today.month
        
        # 월의 첫날과 마지막날 계산
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        logger.info(f"월간 요약 조회: user_id={user_id}, year={year}, month={month}")
        
        # 해당 월의 일기 조회
        entries = (
            db.query(models.DiaryEntry)
            .filter(
                models.DiaryEntry.user_id == user_id,
                models.DiaryEntry.date >= start_date,
                models.DiaryEntry.date <= end_date,
            )
            .all()
        )
        
        # 모드별 분포 계산
        mode_counts: Dict[str, int] = {}
        date_entry_counts: Dict[date, int] = {}
        
        for e in entries:
            if e.mode:
                mode_counts[e.mode] = mode_counts.get(e.mode, 0) + 1
            date_entry_counts[e.date] = date_entry_counts.get(e.date, 0) + 1
        
        # 가장 긴/짧은 일기 찾기
        longest_id, shortest_id = find_longest_shortest_entries(entries)
        
        # 가장 많이 작성한 날 찾기
        most_active_date = max(date_entry_counts, key=date_entry_counts.get) if date_entry_counts else None
        
        # 가장 긍정적인 모드 찾기
        most_positive_mode = get_most_positive_mode(mode_counts)
        
        # 일일 평균 작성량 계산
        total_days = (end_date - start_date).days + 1
        average_entries_per_day = len(entries) / total_days if total_days > 0 else 0.0
        
        # 주간별 분포 계산
        weekly_breakdown = _calculate_weekly_breakdown(entries, start_date, end_date)
        
        logger.info(f"월간 요약 완료: total={len(entries)}, avg_per_day={average_entries_per_day:.2f}")
        
        return schemas.MonthlySummaryResponse(
            startDate=start_date,
            endDate=end_date,
            totalEntries=len(entries),
            modeCounts=mode_counts,
            highlights={
                "longestEntryId": longest_id,
                "shortestEntryId": shortest_id,
                "mostPositiveMode": most_positive_mode,
                "mostActiveDate": most_active_date.isoformat() if most_active_date else None,
            },
            averageEntriesPerDay=round(average_entries_per_day, 2),
            weeklyBreakdown=weekly_breakdown,
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        handle_api_error(
            "월간 요약 조회",
            e,
            logger,
            status_code=status.HTTP_400_BAD_REQUEST,
            custom_message=f"올바르지 않은 날짜 형식입니다. year와 month는 유효한 값이어야 합니다. (입력: year={year}, month={month})"
        )
    except Exception as e:
        handle_api_error("월간 요약 조회", e, logger, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _calculate_weekly_breakdown(entries: List, start_date: date, end_date: date) -> Dict[str, int]:
    """주간별 일기 개수 분포 계산"""
    weekly_breakdown: Dict[str, int] = {}
    current_date = start_date
    week_num = 1
    
    while current_date <= end_date:
        days_from_monday = current_date.weekday()
        week_start = current_date - timedelta(days=days_from_monday)
        week_end = week_start + timedelta(days=6)
        
        # 월 범위 내로 제한
        if week_start < start_date:
            week_start = start_date
        if week_end > end_date:
            week_end = end_date
        
        # 해당 주의 일기 개수 계산
        week_entries = [e for e in entries if week_start <= e.date <= week_end]
        weekly_breakdown[f"Week {week_num}"] = len(week_entries)
        
        current_date = week_end + timedelta(days=1)
        week_num += 1
        
        if week_num > 6:
            break
    
    return weekly_breakdown
