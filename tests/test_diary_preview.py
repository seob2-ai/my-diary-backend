"""
일기 분석 미리보기 API 테스트
"""
import pytest


@pytest.mark.api
class TestDiaryPreview:
    """일기 분석 미리보기 테스트 클래스"""
    
    def test_preview_analysis(self, client, test_user_id):
        """분석 미리보기 테스트"""
        diary_data = {
            "emotion": "기쁨",
            "event": "친구들과 만남",
            "reason": "오랜만에 만나서",
            "insight": "친구의 중요성",
            "tomorrow": "운동하기"
        }
        
        response = client.post(
            "/api/diary/preview",
            json=diary_data,
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert "mode_label" in data
        assert "mode_description" in data
        assert "coaching" in data
        assert "is_ambiguous" in data
        assert "ambiguity_score" in data
        assert "ambiguity_reasons" in data
    
    def test_preview_analysis_short(self, client, test_user_id):
        """짧은 일기 분석 미리보기 테스트"""
        diary_data = {
            "emotion": "기쁨"
        }
        
        response = client.post(
            "/api/diary/preview",
            json=diary_data,
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 짧은 일기는 모호할 수 있음
        assert "is_ambiguous" in data
        assert isinstance(data["is_ambiguous"], bool)
    
    def test_preview_analysis_with_content(self, client, test_user_id):
        """content 필드로 분석 미리보기 테스트"""
        diary_data = {
            "content": "오늘은 정말 좋은 하루였다."
        }
        
        response = client.post(
            "/api/diary/preview",
            json=diary_data,
            headers={"x-user-id": test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data


