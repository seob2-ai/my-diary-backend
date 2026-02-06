"""
요약 API 테스트 (주간/월간)
"""
import pytest
from datetime import date, timedelta
from calendar import monthrange


@pytest.mark.api
class TestSummaryAPI:
    """요약 API 테스트 클래스"""
    
    def test_weekly_summary(self, client, test_user_id, sample_diary_data):
        """주간 요약 테스트"""
        # 이번 주에 일기 몇 개 생성
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        # 월요일부터 오늘까지 일기 생성
        for i in range(min(3, today.weekday() + 1)):
            diary_date = monday + timedelta(days=i)
            client.post(
                "/api/diary",
                json={**sample_diary_data, "date": diary_date.isoformat()},
                headers={"x-user-id": test_user_id}
            )
        
        # 주간 요약 조회
        response = client.get(
            "/api/summary/weekly",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "startDate" in data
        assert "endDate" in data
        assert "totalEntries" in data
        assert "modeCounts" in data
        assert "highlights" in data
        assert data["startDate"] == monday.isoformat()
        assert data["endDate"] == (monday + timedelta(days=6)).isoformat()
    
    def test_monthly_summary_current_month(self, client, test_user_id, sample_diary_data):
        """월간 요약 테스트 (현재 월)"""
        # 이번 달에 일기 몇 개 생성
        today = date.today()
        month_start = date(today.year, today.month, 1)
        _, last_day = monthrange(today.year, today.month)
        month_end = date(today.year, today.month, last_day)
        
        # 월 초, 중, 말에 일기 생성
        test_dates = [
            month_start,
            month_start + timedelta(days=10),
            min(today, month_end)
        ]
        
        for diary_date in test_dates:
            if diary_date <= today:
                client.post(
                    "/api/diary",
                    json={**sample_diary_data, "date": diary_date.isoformat()},
                    headers={"x-user-id": test_user_id}
                )
        
        # 월간 요약 조회
        response = client.get(
            "/api/summary/monthly",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "startDate" in data
        assert "endDate" in data
        assert "totalEntries" in data
        assert "modeCounts" in data
        assert "highlights" in data
        assert "averageEntriesPerDay" in data
        assert "weeklyBreakdown" in data
        assert data["startDate"] == month_start.isoformat()
        assert data["endDate"] == month_end.isoformat()
        assert isinstance(data["averageEntriesPerDay"], float)
        assert isinstance(data["weeklyBreakdown"], dict)
    
    def test_monthly_summary_specific_month(self, client, test_user_id, sample_diary_data):
        """특정 월 요약 테스트"""
        # 2024년 1월 데이터 생성
        test_year = 2024
        test_month = 1
        month_start = date(test_year, test_month, 1)
        _, last_day = monthrange(test_year, test_month)
        month_end = date(test_year, test_month, last_day)
        
        # 1월에 일기 생성
        for i in [1, 10, 20]:
            diary_date = date(test_year, test_month, min(i, last_day))
            client.post(
                "/api/diary",
                json={**sample_diary_data, "date": diary_date.isoformat()},
                headers={"x-user-id": test_user_id}
            )
        
        # 특정 월 요약 조회
        response = client.get(
            f"/api/summary/monthly?year={test_year}&month={test_month}",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["startDate"] == month_start.isoformat()
        assert data["endDate"] == month_end.isoformat()
        assert data["totalEntries"] >= 3
    
    def test_monthly_summary_invalid_date(self, client, test_user_id):
        """잘못된 날짜로 월간 요약 테스트"""
        response = client.get(
            "/api/summary/monthly?year=2024&month=13",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 400
    
    def test_monthly_summary_highlights(self, client, test_user_id):
        """월간 요약 하이라이트 테스트"""
        today = date.today()
        
        # 다양한 길이의 일기 생성
        short_diary = {"emotion": "짧음"}
        long_diary = {
            "emotion": "기쁨" * 10,
            "event": "사건" * 10,
            "reason": "이유" * 10,
            "insight": "인사이트" * 10,
            "tomorrow": "내일" * 10
        }
        
        # 짧은 일기
        client.post(
            "/api/diary",
            json={**short_diary, "date": today.isoformat()},
            headers={"x-user-id": test_user_id}
        )
        
        # 긴 일기
        client.post(
            "/api/diary",
            json={**long_diary, "date": today.isoformat()},
            headers={"x-user-id": test_user_id}
        )
        
        # 월간 요약 조회
        response = client.get(
            "/api/summary/monthly",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        highlights = data["highlights"]
        assert "longestEntryId" in highlights
        assert "shortestEntryId" in highlights
        assert "mostPositiveMode" in highlights


