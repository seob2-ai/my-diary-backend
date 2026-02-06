# tests/test_streak_api.py
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.models import DiaryEntry
from app.database import Base, engine, SessionLocal


@pytest.fixture
def client():
    """테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture
def db():
    """테스트용 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_id():
    """테스트용 사용자 ID"""
    return "test_user_streak"


@pytest.fixture
def consecutive_entries(db, test_user_id):
    """연속 작성 일기 데이터 (7일 연속)"""
    today = date.today()
    entries = []
    
    # 최근 7일 연속 작성
    for i in range(7):
        entry_date = today - timedelta(days=i)
        entries.append(
            DiaryEntry(
                id=f"diary_streak_{i}",
                user_id=test_user_id,
                date=entry_date,
                emotion=f"연속 작성 {i+1}일차",
                mode="REFLECTION"
            )
        )
    
    # 과거에도 연속 작성 기록 (10일 연속)
    for i in range(10):
        entry_date = today - timedelta(days=30 + i)
        entries.append(
            DiaryEntry(
                id=f"diary_past_{i}",
                user_id=test_user_id,
                date=entry_date,
                emotion=f"과거 연속 작성",
                mode="REFLECTION"
            )
        )
    
    # 중간에 끊긴 기록 (3일 연속 후 중단)
    for i in range(3):
        entry_date = today - timedelta(days=50 + i)
        entries.append(
            DiaryEntry(
                id=f"diary_gap_{i}",
                user_id=test_user_id,
                date=entry_date,
                emotion=f"중단된 기록",
                mode="REFLECTION"
            )
        )
    
    for entry in entries:
        db.add(entry)
    db.commit()
    
    return entries


@pytest.fixture
def scattered_entries(db, test_user_id):
    """불규칙한 작성 패턴 (연속 없음)"""
    today = date.today()
    entries = []
    
    # 불규칙하게 작성 (1일, 5일, 10일, 15일, 20일 전)
    dates = [today - timedelta(days=d) for d in [1, 5, 10, 15, 20]]
    
    for i, entry_date in enumerate(dates):
        entries.append(
            DiaryEntry(
                id=f"diary_scattered_{i}",
                user_id=test_user_id,
                date=entry_date,
                emotion=f"불규칙 작성",
                mode="LIGHT_LOG"
            )
        )
    
    for entry in entries:
        db.add(entry)
    db.commit()
    
    return entries


class TestStreakAPI:
    """Streak API 테스트"""
    
    def test_get_streak_consecutive(self, client, db, test_user_id, consecutive_entries):
        """연속 작성 기록 테스트"""
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["current_streak"] == 7  # 최근 7일 연속
        assert data["longest_streak"] == 10  # 과거 10일이 최장 기록
        assert data["total_days"] == 20  # 총 20일 작성
        assert data["weekly_progress"] >= 1  # 이번 주 최소 1일 이상 작성 (주 중간일 수 있음)
        assert isinstance(data["calendar_data"], dict)
        assert len(data["achievement_badges"]) > 0
        assert "first_week" in data["achievement_badges"]
        assert "streak_week" in data["achievement_badges"]
    
    def test_get_streak_no_entries(self, client, db):
        """일기가 없는 경우"""
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": "user_with_no_entries"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["current_streak"] == 0
        assert data["longest_streak"] == 0
        assert data["total_days"] == 0
        assert data["weekly_progress"] == 0
        assert len(data["calendar_data"]) == 0
        assert len(data["achievement_badges"]) == 0
    
    def test_get_streak_scattered(self, client, db, test_user_id, scattered_entries):
        """불규칙한 작성 패턴 테스트"""
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 연속 기록이 없거나 1일
        assert data["current_streak"] <= 1
        assert data["longest_streak"] <= 1
        assert data["total_days"] == 5  # 총 5일 작성
        assert data["weekly_progress"] >= 1  # 이번 주 최소 1일
        assert "first_entry" in data["achievement_badges"]
    
    def test_get_streak_custom_weekly_goal(self, client, db, test_user_id, consecutive_entries):
        """커스텀 주간 목표 테스트"""
        response = client.get(
            "/api/analytics/streak?weekly_goal=5",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["weekly_goal"] == 5
        assert data["weekly_progress"] >= 1  # 이번 주 작성일 수 (주 중간일 수 있어서 최소 1일 이상)
    
    def test_get_streak_calendar_data(self, client, db, test_user_id, consecutive_entries):
        """캘린더 데이터 포함 확인"""
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        calendar = data["calendar_data"]
        assert isinstance(calendar, dict)
        
        # 오늘 날짜가 포함되어야 함
        today_str = date.today().isoformat()
        assert today_str in calendar
        assert calendar[today_str] is True  # 오늘 작성했음
    
    def test_get_streak_badges(self, client, db, test_user_id, consecutive_entries):
        """배지 시스템 테스트"""
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        badges = data["achievement_badges"]
        assert isinstance(badges, list)
        
        # 기본 배지 확인
        assert "first_entry" in badges
        assert "first_week" in badges  # 7일 이상 작성
        assert "streak_week" in badges  # 7일 연속
    
    def test_get_streak_missing_user_id(self, client, db):
        """사용자 ID 누락"""
        response = client.get("/api/analytics/streak")
        
        assert response.status_code == 422
    
    def test_get_streak_invalid_weekly_goal(self, client, db, test_user_id):
        """잘못된 주간 목표 (범위 벗어남)"""
        response = client.get(
            "/api/analytics/streak?weekly_goal=10",
            headers={"x-user_id": test_user_id}
        )
        
        # weekly_goal은 1-7 사이여야 함
        assert response.status_code in [400, 422]
    
    def test_get_streak_first_entry_badge(self, client, db, test_user_id):
        """첫 작성 배지 테스트"""
        today = date.today()
        
        # 첫 일기 생성
        entry = DiaryEntry(
            id="diary_first",
            user_id=test_user_id,
            date=today,
            emotion="첫 일기",
            mode="LIGHT_LOG"
        )
        db.add(entry)
        db.commit()
        
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["current_streak"] == 1
        assert data["total_days"] == 1
        assert "first_entry" in data["achievement_badges"]
    
    def test_get_streak_100_days(self, client, db, test_user_id):
        """100일 달성 배지 테스트"""
        today = date.today()
        entries = []
        
        # 100일 전부터 매일 작성 (100일)
        for i in range(100):
            entry_date = today - timedelta(days=99 - i)
            entries.append(
                DiaryEntry(
                    id=f"diary_100_{i}",
                    user_id=test_user_id,
                    date=entry_date,
                    emotion=f"{i+1}일차",
                    mode="REFLECTION"
                )
            )
        
        for entry in entries:
            db.add(entry)
        db.commit()
        
        response = client.get(
            "/api/analytics/streak",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["current_streak"] == 100
        assert data["longest_streak"] == 100
        assert data["total_days"] == 100
        assert "hundred_days" in data["achievement_badges"]
        assert "streak_century" in data["achievement_badges"]  # 100일 연속
        assert "master_streaker" in data["achievement_badges"]  # 최장 100일

