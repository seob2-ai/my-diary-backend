"""
pytest 설정 및 공통 픽스처
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile

from app.database import Base, get_db
from app.main import app


# 테스트용 데이터베이스 파일 경로
TEST_DB_PATH = tempfile.mktemp(suffix=".db")


@pytest.fixture(scope="function")
def test_db():
    """
    테스트용 데이터베이스 세션 생성
    각 테스트마다 새로운 DB를 생성하고 테스트 후 삭제
    """
    # 테스트용 SQLite 엔진 생성 (메모리 또는 임시 파일)
    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 세션 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 의존성 오버라이드
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # 테스트 후 정리
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # 임시 파일 삭제
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # 의존성 오버라이드 제거
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI 테스트 클라이언트
    """
    return TestClient(app)


@pytest.fixture
def test_user_id():
    """테스트용 사용자 ID"""
    return "test-user-123"


@pytest.fixture
def sample_diary_data():
    """샘플 일기 데이터"""
    return {
        "emotion": "기쁨",
        "event": "친구들과 만남",
        "reason": "오랜만에 만나서",
        "insight": "친구의 중요성을 느꼈다",
        "tomorrow": "운동하기"
    }


@pytest.fixture
def sample_diary_data_full():
    """완전한 샘플 일기 데이터 (모든 필드 포함)"""
    return {
        "emotion": "기쁨과 설렘",
        "event": "새로운 프로젝트 시작",
        "reason": "오랫동안 기다려온 프로젝트였기 때문",
        "insight": "협업의 중요성을 다시 한번 느꼈다",
        "tomorrow": "프로젝트 첫 단계를 완료하고 팀원들과 피드백을 나누겠다"
    }


