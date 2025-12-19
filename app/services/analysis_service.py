# app/services/analysis_service.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Protocol


# ─────────────────────────────────────────
# 1. 입력 타입 프로토콜 (DiaryEntry/DiaryCreate 둘 다 지원)
# ─────────────────────────────────────────

class DiaryLike(Protocol):
    date: Optional[date]
    emotion: Optional[str]
    event: Optional[str]
    reason: Optional[str]
    insight: Optional[str]
    tomorrow: Optional[str]


# ─────────────────────────────────────────
# 2. 모호성 판단 결과 데이터 구조
# ─────────────────────────────────────────

@dataclass
class AmbiguityResult:
    is_ambiguous: bool
    score: float               # 0.0 ~ 1.0 (높을수록 모호)
    reasons: List[str]


# ─────────────────────────────────────────
# 3. 모호성 판단 규칙
#    (지금은 MVP 버전, 나중에 세밀하게 수정 가능)
# ─────────────────────────────────────────

def _text_len(s: Optional[str]) -> int:
    return len(s.strip()) if s else 0


def detect_ambiguity(diary: DiaryLike) -> AmbiguityResult:
    """
    모호성 판단 규칙 (MVP 버전)

    기준 (초안):
    - 전체 글자 수가 너무 짧으면 모호
    - 감정/사건/이유 중 비어있는 칸이 많으면 모호
    - 인사이트/내일 한 문장이 모두 비어 있으면 '정리되지 않은 상태'
    """

    reasons: List[str] = []

    emotion_len = _text_len(diary.emotion)
    event_len = _text_len(diary.event)
    reason_len = _text_len(diary.reason)
    insight_len = _text_len(diary.insight)
    tomorrow_len = _text_len(diary.tomorrow)

    total_len = emotion_len + event_len + reason_len + insight_len + tomorrow_len

    # 1) 전체 길이 기준
    if total_len < 20:
        reasons.append("전체 내용이 20자 미만으로 매우 짧아요.")

    # 2) 핵심 층(감정/사건/이유) 비어있는 개수
    core_empty = sum(
        1 for v in [emotion_len, event_len, reason_len]
        if v == 0
    )
    if core_empty >= 2:
        reasons.append("감정·사건·이유 중 두 개 이상이 비어 있어요.")

    # 3) 인사이트/내일 한 문장 미작성
    if insight_len == 0 and tomorrow_len == 0:
        reasons.append("인사이트와 내일의 한 문장이 모두 비어 있어요.")

    # score 계산 (rules 기반 가중치 예시)
    score = 0.0
    if total_len < 20:
        score += 0.5
    if core_empty >= 2:
        score += 0.3
    if insight_len == 0 and tomorrow_len == 0:
        score += 0.2

    # 0.0 ~ 1.0 사이로 clamp
    score = min(1.0, max(0.0, score))

    is_ambiguous = score >= 0.5 or len(reasons) > 0

    return AmbiguityResult(
        is_ambiguous=is_ambiguous,
        score=score,
        reasons=reasons,
    )


# ─────────────────────────────────────────
# 4. 모드 분석 로직 (MVP)
#    - CIS-10 본격 구현 전에 쓸 수 있는 가벼운 버전
# ─────────────────────────────────────────

def analyze_mode(diary: DiaryLike) -> Dict[str, Any]:
    """
    일기 한 편의 '모드'를 간단히 판정하는 MVP 버전.

    예시 모드:
    - LIGHT_LOG: 짧은 메모 수준
    - EMOTION_DUMP: 감정 위주로 쏟아낸 상태
    - REFLECTION: 이유/인사이트까지 연결된 상태
    - ACTIONABLE: 내일 한 문장까지 구체적인 행동이 나온 상태
    """

    amb = detect_ambiguity(diary)

    emotion_len = _text_len(diary.emotion)
    event_len = _text_len(diary.event)
    reason_len = _text_len(diary.reason)
    insight_len = _text_len(diary.insight)
    tomorrow_len = _text_len(diary.tomorrow)

    filled_core = sum(1 for v in [emotion_len, event_len, reason_len] if v > 0)

    mode = "LIGHT_LOG"
    mode_label = "짧은 기록"
    mode_desc = "간단한 메모 수준의 일기입니다. 감정과 사건을 조금 더 적어 보면 좋아요."

    if amb.is_ambiguous:
        mode = "AMBIGUOUS"
        mode_label = "모호한 기록"
        mode_desc = "내용이 조금 짧거나 핵심 정보가 부족해서, 충분히 정리되지 않은 일기일 수 있어요."
    else:
        if filled_core == 1:
            mode = "EMOTION_DUMP"
            mode_label = "감정 토로 모드"
            mode_desc = "감정이 중심인 일기입니다. 무슨 일이 있었는지, 왜 그런 감정이 들었는지도 조금 적어볼까요?"
        elif filled_core == 2:
            mode = "REFLECTION"
            mode_label = "부분 성찰 모드"
            mode_desc = "감정과 사건/이유가 어느 정도 연결된 상태예요. 인사이트를 한 문장으로 정리해보면 더 좋아요."
        elif filled_core == 3:
            if tomorrow_len > 0:
                mode = "ACTIONABLE"
                mode_label = "행동 기반 성찰 모드"
                mode_desc = "오늘의 감정·사건·이유가 잘 연결되고, 내일의 한 문장까지 정리된 일기입니다."
            else:
                mode = "REFLECTION_DEEP"
                mode_label = "깊은 성찰 모드"
                mode_desc = "감정·사건·이유가 잘 연결된 깊이 있는 일기입니다. 내일의 한 문장을 덧붙이면 더 좋습니다."

    analysis_meta: Dict[str, Any] = {
        "ambiguity": {
            "is_ambiguous": amb.is_ambiguous,
            "score": amb.score,
            "reasons": amb.reasons,
        },
        "lengths": {
            "emotion": emotion_len,
            "event": event_len,
            "reason": reason_len,
            "insight": insight_len,
            "tomorrow": tomorrow_len,
            "total": emotion_len + event_len + reason_len + insight_len + tomorrow_len,
        },
        "core_filled_count": filled_core,
    }

    return {
        "mode": mode,
        "mode_label": mode_label,
        "mode_description": mode_desc,
        "analysis_meta": analysis_meta,
    }


# ─────────────────────────────────────────
# 5. 코칭 메시지 생성 (MVP)
# ─────────────────────────────────────────

def generate_coaching(
    diary: DiaryLike,
    mode: str,
    mode_label: str,
    mode_description: str,
    analysis_meta: Dict[str, Any],
) -> str:
    """
    간단한 규칙 기반 코칭 메시지 (MVP).
    나중에 LLM 기반으로 교체 가능.
    """

    amb = analysis_meta.get("ambiguity", {})
    is_ambiguous = amb.get("is_ambiguous", False)

    if is_ambiguous:
        return (
            "오늘 기록은 아직 조금 추상적인 부분이 있어 보여요. "
            "조금만 더 구체적으로, 어떤 일이 있었는지와 그때 어떤 생각이 들었는지를 한두 문장만 덧붙여 볼까요?"
        )

    if mode == "EMOTION_DUMP":
        return (
            "감정을 잘 꺼내 주었어요. 👏 이제 그 감정이 들게 된 구체적인 장면이나 말, "
            "상황을 한 번만 떠올려 보고, '왜 이렇게 느꼈지?'를 한 문장으로 적어보면 어떨까요?"
        )

    if mode.startswith("REFLECTION"):
        return (
            "오늘을 돌아보는 시선이 잘 느껴지는 기록이에요. ✨ "
            "여기에서 한 걸음 더 나아가, '내가 배운 점 한 가지'를 짧게 정리해 보면 내일의 나에게 큰 도움이 될 거예요."
        )

    if mode == "ACTIONABLE":
        return (
            "감정과 사건, 이유, 그리고 내일의 한 문장까지 멋지게 정리했어요. 🌱 "
            "내일 이 문장을 떠올리기 쉽도록, 잠들기 전에 오늘 쓴 문장을 한 번만 다시 읽어보는 건 어떨까요?"
        )

    # 기본 코칭
    return (
        "오늘 이렇게 기록을 남긴 것만으로도 이미 큰 걸음을 내디딘 거예요. "
        "조금씩, 하지만 꾸준하게 지금의 나를 적어 나가 보아요. 📖"
    )


