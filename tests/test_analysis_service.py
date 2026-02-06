"""
분석 서비스 테스트
"""
import pytest
from app.services.analysis_service import (
    analyze_mode,
    detect_ambiguity,
    generate_coaching
)


@pytest.mark.unit
class TestAnalysisService:
    """분석 서비스 테스트 클래스"""
    
    def test_detect_ambiguity_short(self):
        """짧은 일기 모호성 테스트"""
        class ShortDiary:
            emotion = "기쁨"
            event = ""
            reason = ""
            insight = ""
            tomorrow = ""
            date = None
        
        result = detect_ambiguity(ShortDiary())
        assert result.is_ambiguous is True
        assert result.score > 0
    
    def test_detect_ambiguity_full(self):
        """완전한 일기 모호성 테스트"""
        class FullDiary:
            emotion = "기쁨" * 10
            event = "사건" * 10
            reason = "이유" * 10
            insight = "인사이트" * 10
            tomorrow = "내일" * 10
            date = None
        
        result = detect_ambiguity(FullDiary())
        assert result.is_ambiguous is False
        assert result.score < 0.5
    
    def test_analyze_mode_light_log(self):
        """LIGHT_LOG 모드 테스트"""
        class LightDiary:
            emotion = "기쁨"
            event = ""
            reason = ""
            insight = ""
            tomorrow = ""
            date = None
        
        result = analyze_mode(LightDiary())
        assert "mode" in result
        assert result["mode"] in ["LIGHT_LOG", "AMBIGUOUS"]
    
    def test_analyze_mode_reflection(self):
        """REFLECTION 모드 테스트"""
        class ReflectionDiary:
            emotion = "기쁨" * 5
            event = "사건" * 5
            reason = "이유" * 5
            insight = ""
            tomorrow = ""
            date = None
        
        result = analyze_mode(ReflectionDiary())
        assert "mode" in result
        assert "mode_label" in result
        assert "mode_description" in result
    
    def test_analyze_mode_actionable(self):
        """ACTIONABLE 모드 테스트"""
        class ActionableDiary:
            emotion = "기쁨" * 5
            event = "사건" * 5
            reason = "이유" * 5
            insight = "인사이트" * 5
            tomorrow = "내일" * 5
            date = None
        
        result = analyze_mode(ActionableDiary())
        assert "mode" in result
        # ACTIONABLE 또는 REFLECTION_DEEP일 수 있음
        assert result["mode"] in ["ACTIONABLE", "REFLECTION_DEEP", "REFLECTION"]
    
    def test_generate_coaching(self):
        """코칭 메시지 생성 테스트"""
        class TestDiary:
            emotion = "기쁨"
            event = "사건"
            reason = "이유"
            insight = "인사이트"
            tomorrow = "내일"
            date = None
        
        analysis_meta = {
            "ambiguity": {
                "is_ambiguous": False,
                "score": 0.2,
                "reasons": []
            }
        }
        
        coaching = generate_coaching(
            diary=TestDiary(),
            mode="REFLECTION",
            mode_label="성찰 모드",
            mode_description="설명",
            analysis_meta=analysis_meta
        )
        
        assert isinstance(coaching, str)
        assert len(coaching) > 0


