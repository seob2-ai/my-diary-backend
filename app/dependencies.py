# app/dependencies.py
"""
공통 의존성 함수
"""
from fastapi import Header, HTTPException, status
from typing import Optional


def get_current_user_id(
    x_user_id: str = Header(..., alias="x-user-id", description="사용자 ID")
) -> str:
    """
    x-user-id 헤더에서 사용자 ID를 추출하는 의존성 함수
    
    Args:
        x_user_id: HTTP 헤더에서 추출한 사용자 ID
        
    Returns:
        사용자 ID 문자열
        
    Raises:
        HTTPException: 사용자 ID가 없거나 빈 문자열인 경우 (422)
    """
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "MISSING_USER_ID",
                "message": "X-User-Id 헤더가 필요합니다."
            }
        )
    return x_user_id.strip()


def get_optional_user_id(
    x_user_id: Optional[str] = Header(default=None, alias="x-user-id", description="사용자 ID (선택)")
) -> Optional[str]:
    """
    선택적 사용자 ID 추출 (없어도 에러 발생 안함)
    
    Args:
        x_user_id: HTTP 헤더에서 추출한 사용자 ID (선택)
        
    Returns:
        사용자 ID 문자열 또는 None
    """
    if x_user_id:
        return x_user_id.strip()
    return None


