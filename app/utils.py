# app/utils.py
"""
유틸리티 함수 및 클래스
"""
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, date

from fastapi import HTTPException


class DictLike:
    """
    딕셔너리를 객체처럼 접근할 수 있게 하는 래퍼 클래스
    analysis_service.py의 DiaryLike Protocol과 호환
    """
    def __init__(self, data: Dict[str, Any]):
        self._data = data or {}
    
    @property
    def date(self) -> Optional[str]:
        return self._data.get("date")
    
    @property
    def emotion(self) -> str:
        val = self._data.get("emotion")
        return val if val is not None else ""
    
    @property
    def event(self) -> str:
        val = self._data.get("event")
        return val if val is not None else ""
    
    @property
    def reason(self) -> str:
        val = self._data.get("reason")
        return val if val is not None else ""
    
    @property
    def insight(self) -> str:
        val = self._data.get("insight")
        return val if val is not None else ""
    
    @property
    def tomorrow(self) -> str:
        val = self._data.get("tomorrow")
        return val if val is not None else ""


def parse_date_or_today(date_str: Optional[str]) -> date:
    """
    날짜 문자열을 date 객체로 변환. 없으면 오늘 날짜 반환.
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        
    Returns:
        date 객체
        
    Raises:
        HTTPException: 날짜 형식이 올바르지 않은 경우 (400)
    """
    if not date_str:
        return datetime.now().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요. (입력값: {date_str})"
        )


def parse_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
    default_days: int = 30
) -> tuple[date, date]:
    """
    시작일과 종료일 문자열을 파싱하여 date 객체 튜플로 반환.
    
    Args:
        start_date: YYYY-MM-DD 형식의 시작일 문자열 (None이면 end_date - default_days)
        end_date: YYYY-MM-DD 형식의 종료일 문자열 (None이면 오늘)
        default_days: start_date가 없을 때 기본으로 사용할 일수 (기본값: 30)
        
    Returns:
        (start_date, end_date) 튜플
        
    Raises:
        HTTPException: 
            - 날짜 형식이 올바르지 않은 경우 (400)
            - start_date가 end_date보다 늦은 경우 (400)
    """
    from datetime import timedelta
    
    today = datetime.now().date()
    
    # end_date 파싱
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="end_date 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요."
            )
    else:
        end = today
    
    # start_date 파싱
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="start_date 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요."
            )
    else:
        # 기본값: end_date로부터 default_days 전
        start = end - timedelta(days=default_days)
    
    # 유효성 검증
    if start > end:
        raise HTTPException(
            status_code=400,
            detail="start_date는 end_date보다 이전이어야 합니다."
        )
    
    return start, end


def normalize_analysis_result(raw: Any) -> Dict[str, Any]:
    """
    analyze_mode 반환값을 정규화
    
    Args:
        raw: analyze_mode 함수의 반환값 (dict, tuple, list, 또는 기타)
        
    Returns:
        정규화된 분석 결과 딕셔너리
    """
    if isinstance(raw, dict):
        return raw
    elif isinstance(raw, (tuple, list)):
        return {
            "mode": raw[0] if len(raw) > 0 else None,
            "analysis_meta": raw[1] if len(raw) > 1 else None,
        }
    return {"mode": raw}


def calculate_diary_length(entry) -> int:
    """
    일기 엔트리의 전체 길이 계산
    
    Args:
        entry: DiaryEntry 모델 또는 유사 객체
        
    Returns:
        전체 텍스트 길이
    """
    combined = " ".join([
        entry.emotion or "",
        entry.event or "",
        entry.reason or "",
        entry.insight or "",
        entry.tomorrow or ""
    ]).strip()
    return len(combined)


def find_longest_shortest_entries(entries: List) -> Tuple[Optional[str], Optional[str]]:
    """
    가장 긴/짧은 일기 찾기
    
    Args:
        entries: DiaryEntry 리스트
        
    Returns:
        (longest_id, shortest_id) 튜플
    """
    longest_id = None
    shortest_id = None
    longest_len = -1
    shortest_len = 10**9
    
    for e in entries:
        length = calculate_diary_length(e)
        if length > longest_len:
            longest_len = length
            longest_id = e.id
        if length < shortest_len:
            shortest_len = length
            shortest_id = e.id
    
    return longest_id, shortest_id


def create_diary_like_from_payload(
    payload,
    emotion_override: Optional[str] = None
) -> DictLike:
    """
    DiaryCreate/DiaryUpdate 스키마에서 DictLike 객체 생성
    
    Args:
        payload: DiaryCreate 또는 DiaryUpdate 스키마 인스턴스
        emotion_override: emotion 필드를 덮어쓸 값 (content 필드 매핑용)
        
    Returns:
        DictLike 객체
    """
    emotion = emotion_override or payload.emotion or ""
    # content 필드가 있으면 emotion 필드로 매핑 (클라이언트 호환성)
    if hasattr(payload, 'content') and payload.content and not emotion:
        emotion = payload.content
    
    return DictLike({
        "date": payload.date if hasattr(payload, 'date') else None,
        "emotion": emotion,
        "event": payload.event or "",
        "reason": payload.reason or "",
        "insight": payload.insight or "",
        "tomorrow": payload.tomorrow or "",
    })


def create_diary_like_from_entry(entry) -> DictLike:
    """
    DiaryEntry 모델에서 DictLike 객체 생성
    
    Args:
        entry: DiaryEntry 모델 인스턴스
        
    Returns:
        DictLike 객체
    """
    return DictLike({
        "date": entry.date.isoformat() if entry.date else None,
        "emotion": entry.emotion or "",
        "event": entry.event or "",
        "reason": entry.reason or "",
        "insight": entry.insight or "",
        "tomorrow": entry.tomorrow or "",
    })


def generate_coaching_safely(
    diary_like: DictLike,
    analysis: Dict[str, Any],
    logger: Any = None
) -> Optional[str]:
    """
    코칭 메시지를 안전하게 생성 (예외 처리 포함)
    
    Args:
        diary_like: DiaryLike 프로토콜을 따르는 객체
        analysis: 분석 결과 딕셔너리
        logger: 로거 인스턴스 (선택)
        
    Returns:
        코칭 메시지 문자열 또는 None
    """
    from app.services.analysis_service import generate_coaching
    
    try:
        mode = analysis.get("mode")
        mode_label = analysis.get("mode_label")
        mode_description = analysis.get("mode_description")
        
        if not (mode and mode_label and mode_description):
            return None
        
        coaching_message = generate_coaching(
            diary=diary_like,
            mode=mode,
            mode_label=mode_label,
            mode_description=mode_description,
            analysis_meta=analysis.get("analysis_meta", {}),
        )
        
        if logger:
            logger.info(f"코칭 메시지 생성 완료: {coaching_message[:50]}...")
        
        return coaching_message
    except Exception as e:
        if logger:
            logger.warning(f"코칭 메시지 생성 실패: {type(e).__name__}: {str(e)}")
        return None


def handle_api_error(
    operation_name: str,
    error: Exception,
    logger: Any,
    status_code: int = 500,
    custom_message: Optional[str] = None,
    custom_message_func: Optional[Callable[[Exception], str]] = None,
    include_error_in_message: bool = True,
    rollback_db: Optional[Any] = None
) -> None:
    """
    API 에러를 일관된 방식으로 처리
    
    자동 로깅 (exc_info=True 포함) 및 DB 롤백 지원, 커스텀 메시지 지원
    
    Args:
        operation_name: 작업 이름 (예: "일기 생성", "감정 트렌드 분석")
        error: 발생한 예외
        logger: 로거 인스턴스
        status_code: HTTP 상태 코드 (기본값: 500)
        custom_message: 사용자 정의 에러 메시지 (문자열 또는 포맷 문자열)
            - 문자열: 직접 사용
            - 포맷 문자열: {error}, {error_type}, {operation} 변수 사용 가능
            예: "날짜 형식 오류: {error} (입력: {input_value})"
        custom_message_func: 동적 메시지 생성 함수 (error를 인자로 받음)
            예: lambda e: f"커스텀 메시지: {str(e)}"
        include_error_in_message: 기본 메시지에 에러 내용 포함 여부 (기본값: True)
        rollback_db: DB 세션 (롤백이 필요한 경우)
        
    Raises:
        HTTPException: 변환된 HTTP 예외
        
    Examples:
        # 기본 사용
        handle_api_error("일기 생성", e, logger)
        
        # 커스텀 메시지 (문자열)
        handle_api_error("일기 생성", e, logger, custom_message="일기를 저장할 수 없습니다.")
        
        # 커스텀 메시지 (포맷 문자열)
        handle_api_error(
            "일기 생성", e, logger,
            custom_message="날짜 형식 오류: {error} (입력: {input_value})",
            input_value=date_str
        )
        
        # 동적 메시지 생성 함수
        handle_api_error(
            "일기 생성", e, logger,
            custom_message_func=lambda err: f"상세 오류: {type(err).__name__} - {str(err)}"
        )
    """
    from fastapi import HTTPException
    
    # DB 롤백이 필요한 경우
    rollback_success = False
    if rollback_db:
        try:
            # DB 세션이 활성 상태인지 확인
            if hasattr(rollback_db, 'is_active') and rollback_db.is_active:
                rollback_db.rollback()
                rollback_success = True
                logger.debug(f"{operation_name}: DB 롤백 성공")
            else:
                logger.warning(f"{operation_name}: DB 세션이 비활성 상태입니다. 롤백을 건너뜁니다.")
        except Exception as rollback_error:
            # 롤백 실패 시에도 로깅
            logger.error(
                f"{operation_name}: DB 롤백 실패: {type(rollback_error).__name__}: {str(rollback_error)}",
                exc_info=True
            )
    
    # 자동 로깅 (exc_info=True 포함하여 전체 스택 트레이스 기록)
    logger.error(
        f"{operation_name} 오류: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={
            "operation": operation_name,
            "error_type": type(error).__name__,
            "rollback_attempted": rollback_db is not None,
            "rollback_success": rollback_success
        }
    )
    
    # 에러 메시지 결정
    if custom_message_func:
        # 동적 메시지 생성 함수 사용
        try:
            detail = custom_message_func(error)
        except Exception as func_error:
            logger.warning(
                f"{operation_name}: 커스텀 메시지 함수 실행 실패: {str(func_error)}",
                exc_info=True
            )
            detail = f"{operation_name} 중 오류가 발생했습니다: {str(error)}"
    elif custom_message:
        # 포맷 문자열 처리
        try:
            # 기본 변수들
            format_vars = {
                "error": str(error),
                "error_type": type(error).__name__,
                "operation": operation_name
            }
            
            # 포맷 문자열에 변수가 있는지 확인
            if "{" in custom_message and "}" in custom_message:
                # 포맷 문자열로 처리
                detail = custom_message.format(**format_vars)
            else:
                # 일반 문자열로 처리
                if include_error_in_message:
                    detail = f"{custom_message} (오류: {str(error)})"
                else:
                    detail = custom_message
        except (KeyError, ValueError) as format_error:
            # 포맷 오류 시 원본 메시지 사용
            logger.warning(
                f"{operation_name}: 커스텀 메시지 포맷 오류: {str(format_error)}",
                exc_info=True
            )
            detail = custom_message if not include_error_in_message else f"{custom_message} (오류: {str(error)})"
    else:
        # 기본 메시지
        if include_error_in_message:
            detail = f"{operation_name} 중 오류가 발생했습니다: {str(error)}"
        else:
            detail = f"{operation_name} 중 오류가 발생했습니다."
    
    # HTTPException 발생
    raise HTTPException(
        status_code=status_code,
        detail=detail
    )


def create_empty_emotion_response(
    start: date,
    end: date,
    granularity: str
) -> Any:
    """
    빈 감정 트렌드 응답 생성
    
    Args:
        start: 시작일
        end: 종료일
        granularity: 집계 단위 ("day" | "week" | "month")
        
    Returns:
        EmotionTrendsResponse 스키마 인스턴스
    """
    from app import schemas
    
    return schemas.EmotionTrendsResponse(
        period={
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "granularity": granularity
        },
        emotion_distribution={},
        daily_trends=[],
        insights=["분석할 일기 데이터가 없습니다."],
        average_score=0.0,
        trend="stable"
    )


def create_empty_streak_response(
    weekly_goal: int = None
) -> Any:
    """
    빈 Streak 응답 생성
    
    Args:
        weekly_goal: 주간 목표 작성 수 (None이면 기본값 사용)
        
    Returns:
        StreakResponse 스키마 인스턴스
    """
    from app import schemas
    from app.constants import StreakConstants
    
    if weekly_goal is None:
        weekly_goal = StreakConstants.DEFAULT_WEEKLY_GOAL
    
    return schemas.StreakResponse(
        current_streak=0,
        longest_streak=0,
        total_days=0,
        calendar_data={},
        weekly_goal=weekly_goal,
        weekly_progress=0,
        achievement_badges=[],
        streak_freeze_used=False
    )

