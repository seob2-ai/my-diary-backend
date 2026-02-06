# app/constants.py
"""
애플리케이션 상수 정의
"""
from typing import Dict, Set

# 모드 우선순위 (높을수록 긍정적)
# analysis_service.py에서 정의된 실제 모드 이름 사용
MODE_PRIORITY: Dict[str, int] = {
    "ACTIONABLE": 6,        # 행동 기반 성찰 모드
    "REFLECTION_DEEP": 5,   # 깊은 성찰 모드
    "REFLECTION": 4,        # 부분 성찰 모드
    "EMOTION_DUMP": 3,      # 감정 토로 모드
    "LIGHT_LOG": 2,         # 짧은 기록
    "AMBIGUOUS": 1,         # 모호한 기록
}


# ---------- 감정 분석 키워드 (한국어 기준) ----------
class EmotionKeywords:
    """감정 키워드 상수"""
    POSITIVE: Set[str] = {
        "기쁨", "행복", "즐거움", "설렘", "뿌듯", "만족", "감사", "감동", "희망", "자신감",
        "성취", "성공", "축하", "축하해", "좋아", "좋은", "멋져", "대단", "최고", "완벽",
        "사랑", "따뜻", "평화", "편안", "여유", "안정", "즐거", "신나", "환상", "기대",
        "긍정", "낙관", "낙천", "활기", "에너지", "열정", "의욕", "동기"
    }
    
    NEGATIVE: Set[str] = {
        "슬픔", "우울", "절망", "걱정", "불안", "두려움", "공포", "분노", "짜증", "화남",
        "실망", "후회", "아쉬움", "피곤", "지침", "무기력", "외로움", "고독",
        "스트레스", "압박", "부담", "불편", "답답", "힘듦", "어려움", "고민",
        "염려", "무서움", "패닉", "혼란",
        "미안", "죄송", "원망", "시기", "질투",
        "부정", "비관", "포기", "체념", "무력감"
    }
    
    NEUTRAL: Set[str] = {
        "보통", "평범", "그저그래", "무난", "평온", "일상", "그냥", "별일없",
        "중립", "중성", "특별", "별반", "그럭저럭"
    }


# ---------- Streak 관련 상수 ----------
class StreakConstants:
    """일기 작성 연속성(Streak) 관련 상수"""
    # 시간 단위
    WEEK_DAYS: int = 7
    MONTH_DAYS: int = 30
    CALENDAR_RANGE_DAYS: int = 90  # 캘린더 히트맵 기본 범위
    
    # 배지 달성 기준
    BADGE_THRESHOLDS: Dict[str, int] = {
        "first_entry": 1,           # 첫 일기 작성
        "week_streak": 7,           # 7일 연속 작성
        "month_streak": 30,         # 30일 연속 작성
        "century_streak": 100,      # 100일 연속 작성
        "week_total": 7,            # 총 7일 작성
        "month_total": 30,          # 총 30일 작성
        "century_total": 100        # 총 100일 작성
    }
    
    # 주간 목표 기본값
    DEFAULT_WEEKLY_GOAL: int = 7
    MIN_WEEKLY_GOAL: int = 1
    MAX_WEEKLY_GOAL: int = 7


def get_most_positive_mode(mode_counts: Dict[str, int]) -> str | None:
    """
    모드별 개수에서 가장 긍정적인 모드를 반환
    
    Args:
        mode_counts: 모드별 개수 딕셔너리 {"ACTIONABLE": 3, "REFLECTION": 2, ...}
        
    Returns:
        가장 긍정적인 모드 이름 또는 None
    """
    if not mode_counts:
        return None
    
    return max(
        mode_counts.keys(),
        key=lambda mode: MODE_PRIORITY.get(mode, 0)
    )

