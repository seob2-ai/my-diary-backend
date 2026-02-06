# app/config.py
"""
애플리케이션 설정 관리
환경 변수에서 설정을 읽어옵니다.
"""
import os
from typing import List
from functools import lru_cache

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings:
    """애플리케이션 설정"""
    
    # 환경
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 데이터베이스
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./diary.db")
    
    # CORS 설정
    _ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """CORS 허용 출처 목록"""
        if self._ALLOWED_ORIGINS == "*":
            return ["*"]
        return [
            origin.strip() 
            for origin in self._ALLOWED_ORIGINS.split(",") 
            if origin.strip()
        ]
    
    @property
    def ALLOW_ALL_ORIGINS(self) -> bool:
        """모든 출처 허용 여부"""
        return self._ALLOWED_ORIGINS == "*"
    
    # 로깅
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    # 서버
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    def __repr__(self) -> str:
        return (
            f"Settings("
            f"ENVIRONMENT={self.ENVIRONMENT}, "
            f"DEBUG={self.DEBUG}, "
            f"DATABASE_URL={self.DATABASE_URL}, "
            f"ALLOWED_ORIGINS={self.ALLOWED_ORIGINS})"
        )


@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (캐싱)"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()


