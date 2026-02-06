# tests/test_emotion_analytics.py
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
    return "test_user_emotion"


@pytest.fixture
def sample_entries(db, test_user_id):
    """테스트용 일기 데이터 생성"""
    today = date.today()
    
    # 긍정적 감정 일기들
    entries = [
        DiaryEntry(
            id=f"diary_{i}",
            user_id=test_user_id,
            date=today - timedelta(days=5-i),
            emotion=f"기쁨과 행복으로 가득한 하루였어요. {i}",
            event=f"좋은 일이 있었습니다",
            mode="REFLECTION"
        )
        for i in range(3)
    ]
    
    # 부정적 감정 일기들
    entries.extend([
        DiaryEntry(
            id=f"diary_neg_{i}",
            user_id=test_user_id,
            date=today - timedelta(days=8-i),
            emotion=f"우울하고 힘든 하루였어요. {i}",
            event=f"어려운 일이 있었습니다",
            mode="EMOTION_DUMP"
        )
        for i in range(2)
    ])
    
    # 중립 감정 일기
    entries.append(
        DiaryEntry(
            id="diary_neutral",
            user_id=test_user_id,
            date=today - timedelta(days=10),
            emotion="평범한 하루였습니다",
            event="특별한 일 없음",
            mode="LIGHT_LOG"
        )
    )
    
    for entry in entries:
        db.add(entry)
    db.commit()
    
    return entries


class TestEmotionTrendsAPI:
    """감정 트렌드 분석 API 테스트"""
    
    def test_get_emotion_trends_default(self, client, db, test_user_id, sample_entries):
        """기본 파라미터로 감정 트렌드 조회"""
        response = client.get(
            "/api/analytics/emotion-trends",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "emotion_distribution" in data
        assert "daily_trends" in data
        assert "insights" in data
        assert "average_score" in data
        assert "trend" in data
        
        assert isinstance(data["daily_trends"], list)
        assert len(data["daily_trends"]) > 0
        
        # 평균 점수는 -1.0 ~ 1.0 범위
        assert -1.0 <= data["average_score"] <= 1.0
    
    def test_get_emotion_trends_with_dates(self, client, db, test_user_id, sample_entries):
        """날짜 범위 지정하여 조회"""
        today = date.today()
        start_date = (today - timedelta(days=10)).isoformat()
        end_date = today.isoformat()
        
        response = client.get(
            f"/api/analytics/emotion-trends?start_date={start_date}&end_date={end_date}",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"]["start_date"] == start_date
        assert data["period"]["end_date"] == end_date
    
    def test_get_emotion_trends_week_granularity(self, client, db, test_user_id, sample_entries):
        """주별 집계 테스트"""
        response = client.get(
            "/api/analytics/emotion-trends?granularity=week",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"]["granularity"] == "week"
        assert isinstance(data["daily_trends"], list)
    
    def test_get_emotion_trends_month_granularity(self, client, db, test_user_id, sample_entries):
        """월별 집계 테스트"""
        response = client.get(
            "/api/analytics/emotion-trends?granularity=month",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"]["granularity"] == "month"
    
    def test_get_emotion_trends_no_data(self, client, db):
        """데이터가 없는 경우"""
        response = client.get(
            "/api/analytics/emotion-trends",
            headers={"x-user-id": "user_with_no_data"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["daily_trends"]) == 0
        assert data["average_score"] == 0.0
        assert "분석할 일기 데이터가 없습니다" in data["insights"][0]
    
    def test_get_emotion_trends_invalid_date_format(self, client, db, test_user_id):
        """잘못된 날짜 형식"""
        response = client.get(
            "/api/analytics/emotion-trends?start_date=invalid",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 400
    
    def test_get_emotion_trends_missing_user_id(self, client, db):
        """사용자 ID 누락"""
        response = client.get("/api/analytics/emotion-trends")
        
        assert response.status_code == 422
    
    def test_get_emotion_trends_invalid_granularity(self, client, db, test_user_id):
        """잘못된 granularity"""
        response = client.get(
            "/api/analytics/emotion-trends?granularity=invalid",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 422
    
    def test_emotion_distribution_counts(self, client, db, test_user_id, sample_entries):
        """감정 분포 카운트 확인"""
        response = client.get(
            "/api/analytics/emotion-trends",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        distribution = data["emotion_distribution"]
        
        # positive, neutral, negative 키가 있어야 함
        assert "positive" in distribution or "negative" in distribution or "neutral" in distribution
        
        # 합계가 일기 개수와 일치해야 함
        total = sum(distribution.values())
        assert total == len(sample_entries)
    
    def test_emotion_insights_generation(self, client, db, test_user_id, sample_entries):
        """인사이트 생성 확인"""
        response = client.get(
            "/api/analytics/emotion-trends",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["insights"], list)
        assert len(data["insights"]) > 0


