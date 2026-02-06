"""
일기 API 테스트
"""
import pytest
from datetime import date, timedelta
from app import models


@pytest.mark.api
class TestDiaryAPI:
    """일기 API 테스트 클래스"""
    
    def test_create_diary(self, client, test_user_id, sample_diary_data):
        """일기 생성 테스트"""
        response = client.post(
            "/api/diary",
            json=sample_diary_data,
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["emotion"] == sample_diary_data["emotion"]
        assert data["mode"] is not None  # 분석 모드가 자동으로 설정되어야 함
        assert data["coaching"] is not None  # 코칭 메시지가 생성되어야 함
    
    def test_create_diary_with_content_field(self, client, test_user_id):
        """content 필드만 있는 경우 테스트 (클라이언트 호환성)"""
        response = client.post(
            "/api/diary",
            json={"content": "오늘은 정말 좋은 하루였다."},
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_list_diaries(self, client, test_user_id, sample_diary_data):
        """일기 목록 조회 테스트"""
        # 먼저 일기 생성
        create_response = client.post(
            "/api/diary",
            json=sample_diary_data,
            headers={"x-user-id": test_user_id}
        )
        assert create_response.status_code == 201
        
        # 목록 조회
        response = client.get(
            "/api/diary",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_diaries_with_date_filter(self, client, test_user_id, sample_diary_data):
        """날짜 필터링 테스트"""
        # 오늘 날짜로 일기 생성
        create_response = client.post(
            "/api/diary",
            json={**sample_diary_data, "date": date.today().isoformat()},
            headers={"x-user-id": test_user_id}
        )
        assert create_response.status_code == 201
        
        # 오늘 날짜로 필터링
        response = client.get(
            f"/api/diary?date={date.today().isoformat()}",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_get_diary_by_id(self, client, test_user_id, sample_diary_data):
        """일기 단건 조회 테스트"""
        # 일기 생성
        create_response = client.post(
            "/api/diary",
            json=sample_diary_data,
            headers={"x-user-id": test_user_id}
        )
        assert create_response.status_code == 201
        diary_id = create_response.json()["id"]
        
        # 단건 조회
        response = client.get(
            f"/api/diary/{diary_id}",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == diary_id
        assert data["emotion"] == sample_diary_data["emotion"]
    
    def test_update_diary(self, client, test_user_id, sample_diary_data):
        """일기 수정 테스트"""
        # 일기 생성
        create_response = client.post(
            "/api/diary",
            json=sample_diary_data,
            headers={"x-user-id": test_user_id}
        )
        assert create_response.status_code == 201
        diary_id = create_response.json()["id"]
        
        # 일기 수정
        update_data = {"emotion": "수정된 감정"}
        response = client.patch(
            f"/api/diary/{diary_id}",
            json=update_data,
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["emotion"] == "수정된 감정"
        # 수정 시 분석 모드가 재계산되어야 함
        assert data["mode"] is not None
    
    def test_delete_diary(self, client, test_user_id, sample_diary_data):
        """일기 삭제 테스트"""
        # 일기 생성
        create_response = client.post(
            "/api/diary",
            json=sample_diary_data,
            headers={"x-user-id": test_user_id}
        )
        assert create_response.status_code == 201
        diary_id = create_response.json()["id"]
        
        # 일기 삭제
        response = client.delete(
            f"/api/diary/{diary_id}",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = client.get(
            f"/api/diary/{diary_id}",
            headers={"x-user-id": test_user_id}
        )
        assert get_response.status_code == 404
    
    def test_invalid_date_format(self, client, test_user_id):
        """잘못된 날짜 형식 테스트"""
        response = client.get(
            "/api/diary?date=invalid-date",
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "message" in data
    
    def test_missing_user_id(self, client, sample_diary_data):
        """사용자 ID 누락 테스트"""
        response = client.post(
            "/api/diary",
            json=sample_diary_data
        )
        
        assert response.status_code == 422  # Validation error

