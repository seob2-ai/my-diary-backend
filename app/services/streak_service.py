# app/services/streak_service.py
"""
일기 작성 연속성(Streak) 계산 서비스
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple, Set

from ..constants import StreakConstants


def calculate_streak(dates: List[date], today: date = None) -> Tuple[int, int]:
    """
    연속 작성 일수 계산
    
    Args:
        dates: 일기 작성 날짜 리스트 (정렬 필요)
        today: 오늘 날짜 (기본값: date.today())
        
    Returns:
        (current_streak, longest_streak) 튜플
        - current_streak: 현재 연속 작성 일수 (오늘 포함하여 연속된 날짜 수)
        - longest_streak: 최장 연속 작성 일수
    """
    if today is None:
        today = date.today()
    
    if not dates:
        return 0, 0
    
    # 날짜 정렬 및 중복 제거
    sorted_dates = sorted(set(dates))
    
    # 최장 연속 기록 계산
    longest_streak = 0
    current_streak_temp = 1
    
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            current_streak_temp += 1
        else:
            longest_streak = max(longest_streak, current_streak_temp)
            current_streak_temp = 1
    
    longest_streak = max(longest_streak, current_streak_temp)
    
    # 현재 연속 기록 계산 (오늘부터 역순으로 계산)
    current_streak = 0
    check_date = today
    
    # 오늘이 작성되었는지 확인
    date_set = set(sorted_dates)
    
    while check_date in date_set:
        current_streak += 1
        check_date -= timedelta(days=1)
    
    # 어제까지 연속되었다면 오늘도 카운트 (오늘 작성 안 했어도 연속 기록 유지)
    # 하지만 일반적으로는 오늘 작성해야 연속 기록으로 인정
    # 여기서는 오늘 작성했을 때만 연속 기록으로 카운트
    
    return current_streak, longest_streak


def get_calendar_data(
    dates: List[date],
    start_date: date = None,
    end_date: date = None
) -> Dict[str, bool]:
    """
    캘린더 히트맵용 데이터 생성
    
    Args:
        dates: 일기 작성 날짜 리스트
        start_date: 시작 날짜 (기본값: 가장 오래된 날짜의 30일 전)
        end_date: 종료 날짜 (기본값: 오늘)
        
    Returns:
        날짜 문자열을 키로, 작성 여부(bool)를 값으로 하는 딕셔너리
    """
    if not dates:
        return {}
    
    if end_date is None:
        end_date = date.today()
    
    if start_date is None:
        oldest_date = min(dates)
        # 최소 범위로 확장 (또는 첫 작성일로)
        start_date = min(oldest_date, end_date - timedelta(days=StreakConstants.CALENDAR_RANGE_DAYS))
    
    date_set = set(dates)
    calendar_data = {}
    
    current = start_date
    while current <= end_date:
        calendar_data[current.isoformat()] = current in date_set
        current += timedelta(days=1)
    
    return calendar_data


def calculate_weekly_progress(dates: List[date], today: date = None) -> int:
    """
    이번 주 작성 일수 계산 (월요일 시작)
    
    Args:
        dates: 일기 작성 날짜 리스트
        today: 오늘 날짜 (기본값: date.today())
        
    Returns:
        이번 주 작성 일수
    """
    if today is None:
        today = date.today()
    
    # 이번 주 월요일 계산
    days_from_monday = today.weekday()
    week_start = today - timedelta(days=days_from_monday)
    week_end = week_start + timedelta(days=6)
    
    date_set = set(dates)
    count = 0
    
    current = week_start
    while current <= week_end:
        if current in date_set:
            count += 1
        current += timedelta(days=1)
    
    return count


def calculate_achievement_badges(
    total_days: int,
    longest_streak: int,
    current_streak: int
) -> List[str]:
    """
    달성 배지 계산
    
    Args:
        total_days: 총 작성 일수
        longest_streak: 최장 연속 기록
        current_streak: 현재 연속 기록
        
    Returns:
        달성한 배지 리스트
    """
    badges = []
    
    # 첫 작성
    if total_days >= 1:
        badges.append("first_entry")
    
    # 첫 주 완성
    if total_days >= StreakConstants.BADGE_THRESHOLDS["week_total"]:
        badges.append("first_week")
    
    # 첫 달 완성
    if total_days >= StreakConstants.BADGE_THRESHOLDS["month_total"]:
        badges.append("one_month")
    
    # 100일 달성
    if total_days >= StreakConstants.BADGE_THRESHOLDS["century_total"]:
        badges.append("hundred_days")
    
    # 연속 기록 배지
    if current_streak >= StreakConstants.BADGE_THRESHOLDS["week_streak"]:
        badges.append("streak_week")
    if current_streak >= StreakConstants.BADGE_THRESHOLDS["month_streak"]:
        badges.append("streak_month")
    if current_streak >= StreakConstants.BADGE_THRESHOLDS["century_streak"]:
        badges.append("streak_century")
    
    # 최장 기록 배지
    if longest_streak >= StreakConstants.BADGE_THRESHOLDS["month_streak"]:
        badges.append("legendary_streak")
    if longest_streak >= StreakConstants.BADGE_THRESHOLDS["century_streak"]:
        badges.append("master_streaker")
    
    return badges


def get_streak_insights(
    current_streak: int,
    longest_streak: int,
    total_days: int,
    weekly_progress: int,
    weekly_goal: int = 7
) -> List[str]:
    """
    Streak 인사이트 메시지 생성
    
    Args:
        current_streak: 현재 연속 기록
        longest_streak: 최장 연속 기록
        total_days: 총 작성 일수
        weekly_progress: 주간 진행도
        weekly_goal: 주간 목표
        
    Returns:
        인사이트 메시지 리스트
    """
    insights = []
    
    if current_streak == 0:
        insights.append("일기 작성을 시작해보세요! 꾸준함이 습관을 만듭니다.")
    elif current_streak == 1:
        insights.append("첫 날 완료! 내일도 계속해보세요.")
    elif current_streak < StreakConstants.BADGE_THRESHOLDS["week_streak"]:
        remaining = StreakConstants.BADGE_THRESHOLDS["week_streak"] - current_streak
        insights.append(f"{current_streak}일 연속 기록 중입니다! 일주일 목표까지 {remaining}일 남았어요.")
    elif current_streak == StreakConstants.BADGE_THRESHOLDS["week_streak"]:
        insights.append("🎉 일주일 연속 기록 달성! 멋져요!")
    elif current_streak < StreakConstants.BADGE_THRESHOLDS["month_streak"]:
        insights.append(f"{current_streak}일 연속 기록 중입니다! 한 달 목표에 가까워지고 있어요.")
    elif current_streak >= StreakConstants.BADGE_THRESHOLDS["month_streak"]:
        insights.append(f"🔥 {current_streak}일 연속 기록! 정말 대단합니다!")
    
    if longest_streak > current_streak:
        insights.append(f"최장 기록은 {longest_streak}일입니다. 다시 도전해보세요!")
    
    # 주간 목표 관련
    if weekly_progress >= weekly_goal:
        insights.append(f"이번 주 목표 달성! {weekly_progress}일 작성하셨네요.")
    elif weekly_progress > 0:
        remaining = weekly_goal - weekly_progress
        insights.append(f"이번 주 목표까지 {remaining}일 남았어요. 화이팅!")
    
    # 총 작성일 관련
    if total_days >= StreakConstants.BADGE_THRESHOLDS["century_total"]:
        insights.append(f"총 {total_days}일 작성하셨네요! 정말 꾸준하시는군요.")
    elif total_days >= StreakConstants.BADGE_THRESHOLDS["month_total"]:
        insights.append(f"총 {total_days}일 작성했습니다. 좋은 습관이 되어가고 있어요!")
    
    if not insights:
        insights.append("일기 작성 습관을 시작해보세요!")
    
    return insights

