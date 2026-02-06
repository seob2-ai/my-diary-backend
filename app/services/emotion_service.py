# app/services/emotion_service.py
"""
감정 분석 및 점수화 서비스
"""
from typing import Dict, List, Tuple, Optional, Any
from datetime import date, timedelta
from collections import defaultdict

from ..constants import EmotionKeywords


def calculate_emotion_score(text: Optional[str]) -> Tuple[float, str]:
    """
    감정 텍스트를 분석하여 점수(-1.0 ~ 1.0)와 주요 감정 반환
    
    Args:
        text: 감정 필드 텍스트
        
    Returns:
        (emotion_score, dominant_emotion) 튜플
        - emotion_score: -1.0 (매우 부정) ~ 1.0 (매우 긍정)
        - dominant_emotion: "positive" | "neutral" | "negative"
    """
    if not text or not text.strip():
        return 0.0, "neutral"
    
    text_lower = text.lower()
    
    positive_count = sum(1 for keyword in EmotionKeywords.POSITIVE if keyword in text_lower)
    negative_count = sum(1 for keyword in EmotionKeywords.NEGATIVE if keyword in text_lower)
    neutral_count = sum(1 for keyword in EmotionKeywords.NEUTRAL if keyword in text_lower)
    
    # 총 키워드 수
    total_keywords = positive_count + negative_count + neutral_count
    
    if total_keywords == 0:
        # 키워드가 없으면 텍스트 길이와 내용으로 추정
        # 간단한 추정: 긍정적 단어/부정적 단어가 포함된 경우
        if any(word in text_lower for word in ["안", "없", "못", "안", "별로", "싫"]):
            return -0.3, "negative"
        elif any(word in text_lower for word in ["좋", "행복", "기쁨", "만족"]):
            return 0.3, "positive"
        else:
            return 0.0, "neutral"
    
    # 점수 계산: (긍정 - 부정) / 총 키워드
    score = (positive_count - negative_count) / max(total_keywords, 1)
    
    # 점수 범위를 -1.0 ~ 1.0으로 정규화
    score = max(-1.0, min(1.0, score))
    
    # 주요 감정 판단
    if positive_count > negative_count:
        dominant = "positive"
    elif negative_count > positive_count:
        dominant = "negative"
    else:
        dominant = "neutral"
    
    return score, dominant


def extract_emotion_keywords(text: Optional[str]) -> List[str]:
    """
    텍스트에서 감정 키워드 추출
    
    Args:
        text: 감정 텍스트
        
    Returns:
        감정 키워드 리스트
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    all_keywords = EmotionKeywords.POSITIVE | EmotionKeywords.NEGATIVE | EmotionKeywords.NEUTRAL
    
    for keyword in all_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def categorize_emotion(score: float) -> str:
    """
    감정 점수를 카테고리로 변환
    
    Args:
        score: 감정 점수 (-1.0 ~ 1.0)
        
    Returns:
        카테고리: "very_positive" | "positive" | "neutral" | "negative" | "very_negative"
    """
    if score >= 0.7:
        return "very_positive"
    elif score >= 0.3:
        return "positive"
    elif score >= -0.3:
        return "neutral"
    elif score >= -0.7:
        return "negative"
    else:
        return "very_negative"


def get_emotion_label_ko(category: str) -> str:
    """
    감정 카테고리를 한국어 레이블로 변환
    """
    labels = {
        "very_positive": "매우 긍정적",
        "positive": "긍정적",
        "neutral": "중립적",
        "negative": "부정적",
        "very_negative": "매우 부정적"
    }
    return labels.get(category, "중립적")


def calculate_trend(current_scores: List[float], previous_scores: List[float]) -> str:
    """
    감정 트렌드 계산 (increasing, stable, decreasing)
    
    Args:
        current_scores: 현재 기간 점수 리스트
        previous_scores: 이전 기간 점수 리스트
        
    Returns:
        "increasing" | "stable" | "decreasing"
    """
    if not previous_scores:
        return "stable"
    
    current_avg = sum(current_scores) / len(current_scores) if current_scores else 0.0
    previous_avg = sum(previous_scores) / len(previous_scores) if previous_scores else 0.0
    
    diff = current_avg - previous_avg
    
    if abs(diff) < 0.1:  # 0.1 미만 차이는 stable
        return "stable"
    elif diff > 0:
        return "increasing"
    else:
        return "decreasing"


def generate_emotion_insights(
    daily_trends: List[Dict],
    emotion_distribution: Dict[str, int],
    period_days: int
) -> List[str]:
    """
    감정 트렌드 데이터로부터 인사이트 생성
    
    Args:
        daily_trends: 일별 트렌드 데이터
        emotion_distribution: 감정 분포 딕셔너리
        period_days: 분석 기간 (일수)
        
    Returns:
        인사이트 문자열 리스트
    """
    insights = []
    
    if not daily_trends:
        return ["분석할 데이터가 없습니다."]
    
    # 전체 평균 점수 계산
    scores = [day.get("emotion_score", 0.0) for day in daily_trends if day.get("emotion_score")]
    if scores:
        avg_score = sum(scores) / len(scores)
        if avg_score > 0.5:
            insights.append(f"이번 기간 평균 감정 점수가 {avg_score:.2f}로 매우 긍정적입니다. 좋은 일들이 많으셨나요?")
        elif avg_score < -0.5:
            insights.append(f"이번 기간 평균 감정 점수가 {avg_score:.2f}로 다소 부정적입니다. 무언가 힘든 일이 있었나요?")
    
    # 감정 분포 분석
    total = sum(emotion_distribution.values())
    if total > 0:
        positive_ratio = (emotion_distribution.get("positive", 0) + emotion_distribution.get("very_positive", 0)) / total
        if positive_ratio > 0.6:
            insights.append(f"긍정적 감정이 {positive_ratio*100:.0f}%를 차지합니다. 긍정적인 에너지가 넘치시네요!")
        elif positive_ratio < 0.3:
            insights.append(f"부정적 감정이 {(1-positive_ratio)*100:.0f}%로 높습니다. 자신을 돌보는 시간이 필요할 수 있어요.")
    
    # 트렌드 분석
    if len(scores) >= 7:  # 최소 7일 데이터 필요
        first_week_avg = sum(scores[:7]) / 7
        last_week_avg = sum(scores[-7:]) / 7
        
        if last_week_avg > first_week_avg + 0.2:
            insights.append("최근 일주일 동안 감정 점수가 크게 향상되었습니다. 계속 좋은 에너지를 유지해보세요!")
        elif last_week_avg < first_week_avg - 0.2:
            insights.append("최근 일주일 동안 감정 점수가 하락했습니다. 무언가 스트레스를 받고 있나요?")
    
    # 가장 긍정적/부정적 날 찾기
    if daily_trends:
        max_day = max(daily_trends, key=lambda x: x.get("emotion_score", 0.0))
        min_day = min(daily_trends, key=lambda x: x.get("emotion_score", 0.0))
        
        if max_day.get("emotion_score", 0.0) > 0.7:
            insights.append(f"{max_day.get('date')}에 가장 긍정적인 감정을 느꼈습니다.")
        if min_day.get("emotion_score", 0.0) < -0.5:
            insights.append(f"{min_day.get('date')}에 감정이 낮았습니다. 그 날 무슨 일이 있었나요?")
    
    if not insights:
        insights.append("일기 작성이 꾸준하시네요! 감정 변화를 계속 기록해보세요.")
    
    return insights


def calculate_emotion_distribution(entries: List[Any]) -> Dict[str, int]:
    """
    일기 엔트리 리스트에서 감정 분포 계산
    
    Args:
        entries: DiaryEntry 모델 리스트
        
    Returns:
        {"positive": int, "negative": int, "neutral": int} 딕셔너리
    """
    emotion_distribution = defaultdict(int)
    
    for entry in entries:
        if entry.emotion:
            score, _ = calculate_emotion_score(entry.emotion)
            category = categorize_emotion(score)
            if category in ["very_positive", "positive"]:
                emotion_distribution["positive"] += 1
            elif category in ["very_negative", "negative"]:
                emotion_distribution["negative"] += 1
            else:
                emotion_distribution["neutral"] += 1
    
    return dict(emotion_distribution)


def aggregate_emotion_data(entries: List[Any]) -> Tuple[Dict[date, List[float]], List[float], Dict[str, int]]:
    """
    일기 엔트리 리스트에서 일별 감정 데이터 집계
    
    Args:
        entries: DiaryEntry 모델 리스트
        
    Returns:
        (daily_data, all_scores, emotion_distribution) 튜플
        - daily_data: Dict[date, List[float]] - 날짜별 감정 점수 리스트
        - all_scores: List[float] - 모든 감정 점수 리스트
        - emotion_distribution: Dict[str, int] - 감정 분포
    """
    daily_data: Dict[date, List[float]] = defaultdict(list)
    emotion_distribution = defaultdict(int)
    all_scores = []
    
    for entry in entries:
        if entry.emotion:
            score, _ = calculate_emotion_score(entry.emotion)
            daily_data[entry.date].append(score)
            all_scores.append(score)
            
            # 감정 분포 카운트
            category = categorize_emotion(score)
            if category in ["very_positive", "positive"]:
                emotion_distribution["positive"] += 1
            elif category in ["very_negative", "negative"]:
                emotion_distribution["negative"] += 1
            else:
                emotion_distribution["neutral"] += 1
    
    return dict(daily_data), all_scores, dict(emotion_distribution)


def _calculate_dominant_emotion_for_period(entries: List[Any], start_date: date, end_date: date) -> str:
    """
    특정 기간의 일기 엔트리에서 주요 감정 계산
    
    Args:
        entries: DiaryEntry 모델 리스트
        start_date: 시작일
        end_date: 종료일
        
    Returns:
        "positive" | "neutral" | "negative"
    """
    period_emotions = [
        e.emotion for e in entries
        if e.emotion and start_date <= e.date <= end_date
    ]
    
    if not period_emotions:
        return "neutral"
    
    combined_text = " ".join(period_emotions)
    _, dominant = calculate_emotion_score(combined_text)
    return dominant


def aggregate_by_day(
    daily_data: Dict[date, List[float]],
    entries: List[Any],
    start: date,
    end: date
) -> List[Dict[str, Any]]:
    """
    일별 감정 트렌드 집계
    
    Args:
        daily_data: 날짜별 감정 점수 딕셔너리
        entries: DiaryEntry 모델 리스트
        start: 시작일
        end: 종료일
        
    Returns:
        DailyEmotionTrend 형태의 딕셔너리 리스트
    """
    daily_trends = []
    current_date = start
    
    while current_date <= end:
        scores = daily_data.get(current_date, [])
        if scores:
            avg_score = sum(scores) / len(scores)
            category = categorize_emotion(avg_score)
            dominant = _calculate_dominant_emotion_for_period(entries, current_date, current_date)
            
            daily_trends.append({
                "entry_date": current_date,
                "emotion_score": round(avg_score, 2),
                "dominant_emotion": dominant,
                "entry_count": len(scores),
                "emotion_category": category
            })
        
        current_date += timedelta(days=1)
    
    return daily_trends


def aggregate_by_week(
    daily_data: Dict[date, List[float]],
    entries: List[Any],
    start: date,
    end: date
) -> List[Dict[str, Any]]:
    """
    주별 감정 트렌드 집계 (월요일 기준)
    
    Args:
        daily_data: 날짜별 감정 점수 딕셔너리
        entries: DiaryEntry 모델 리스트
        start: 시작일
        end: 종료일
        
    Returns:
        DailyEmotionTrend 형태의 딕셔너리 리스트
    """
    weekly_trends = []
    current_date = start
    
    # 첫 주의 월요일 찾기
    days_from_monday = current_date.weekday()
    week_start = current_date - timedelta(days=days_from_monday)
    
    while week_start <= end:
        week_end = week_start + timedelta(days=6)
        
        week_scores = []
        week_entries_count = 0
        
        check_date = week_start
        while check_date <= week_end and check_date <= end:
            if check_date >= start:
                scores = daily_data.get(check_date, [])
                week_scores.extend(scores)
                week_entries_count += len(scores)
            check_date += timedelta(days=1)
        
        if week_scores:
            avg_score = sum(week_scores) / len(week_scores)
            category = categorize_emotion(avg_score)
            dominant = _calculate_dominant_emotion_for_period(entries, week_start, week_end)
            
            weekly_trends.append({
                "entry_date": week_start,
                "emotion_score": round(avg_score, 2),
                "dominant_emotion": dominant,
                "entry_count": week_entries_count,
                "emotion_category": category
            })
        
        week_start += timedelta(days=7)
    
    return weekly_trends


def aggregate_by_month(
    daily_data: Dict[date, List[float]],
    entries: List[Any],
    start: date,
    end: date
) -> List[Dict[str, Any]]:
    """
    월별 감정 트렌드 집계
    
    Args:
        daily_data: 날짜별 감정 점수 딕셔너리
        entries: DiaryEntry 모델 리스트
        start: 시작일
        end: 종료일
        
    Returns:
        DailyEmotionTrend 형태의 딕셔너리 리스트
    """
    monthly_trends = []
    current_date = start
    
    while current_date <= end:
        # 월의 첫날과 마지막날
        month_start = date(current_date.year, current_date.month, 1)
        if month_start < start:
            month_start = start
        
        # 다음 달 첫날 - 1일
        if current_date.month == 12:
            next_month_start = date(current_date.year + 1, 1, 1)
        else:
            next_month_start = date(current_date.year, current_date.month + 1, 1)
        
        month_end = next_month_start - timedelta(days=1)
        if month_end > end:
            month_end = end
        
        month_scores = []
        month_entries_count = 0
        
        check_date = month_start
        while check_date <= month_end:
            scores = daily_data.get(check_date, [])
            month_scores.extend(scores)
            month_entries_count += len(scores)
            check_date += timedelta(days=1)
        
        if month_scores:
            avg_score = sum(month_scores) / len(month_scores)
            category = categorize_emotion(avg_score)
            dominant = _calculate_dominant_emotion_for_period(entries, month_start, month_end)
            
            monthly_trends.append({
                "entry_date": month_start,
                "emotion_score": round(avg_score, 2),
                "dominant_emotion": dominant,
                "entry_count": month_entries_count,
                "emotion_category": category
            })
        
        # 다음 달로 이동
        current_date = next_month_start
    
    return monthly_trends


def aggregate_by_granularity(
    daily_data: Dict[date, List[float]],
    entries: List[Any],
    start: date,
    end: date,
    granularity: str
) -> List[Dict[str, Any]]:
    """
    Granularity에 따라 감정 트렌드 집계
    
    Args:
        daily_data: 날짜별 감정 점수 딕셔너리
        entries: DiaryEntry 모델 리스트
        start: 시작일
        end: 종료일
        granularity: "day" | "week" | "month"
        
    Returns:
        DailyEmotionTrend 형태의 딕셔너리 리스트
    """
    if granularity == "day":
        return aggregate_by_day(daily_data, entries, start, end)
    elif granularity == "week":
        return aggregate_by_week(daily_data, entries, start, end)
    elif granularity == "month":
        return aggregate_by_month(daily_data, entries, start, end)
    else:
        raise ValueError(f"지원하지 않는 granularity: {granularity}")

