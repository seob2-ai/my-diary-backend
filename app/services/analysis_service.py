# app/services/analysis_service.py

from __future__ import annotations

from typing import Any, Dict, Optional
import re
from dataclasses import dataclass


# ================================
# 0. 설정값 / 키워드 모음 (여기만 나중에 튜닝해도 됨)
# ================================

NEGATIVE_WORDS = [
    "불안", "초조", "우울", "슬픔", "서운", "실망", "후회",
    "힘들", "힘들었", "지침", "지쳤", "무기력", "짜증", "걱정", "스트레스",
]

POSITIVE_WORDS = [
    "행복", "행복했", "기뻤", "즐거웠", "좋았", "좋았다", "편안", "안정",
    "설렜", "재밌었", "감사", "뿌듯",
]

STRONG_NEGATIVE_PATTERNS = [
    "너무 힘들", "버티기 힘들", "더 이상", "한계", "폭발할 것 같",
]

STRONG_POSITIVE_PATTERNS = [
    "정말 좋았", "완전 좋았", "완전 행복", "너무 좋았", "최고였",
]

EVENT_CONCRETE_HINTS = [
    "오늘", "어제", "아침", "점심", "저녁", "퇴근", "출근", "회사", "집",
    "학교", "카페", "친구", "가족", "상사", "회의", "발표", "만났", "갔다", "했다",
]

REASON_LOGIC_WORDS = [
    "때문", "그래서", "왜냐하면", "덕분에", "결과적으로", "그래도",
]

INSIGHT_DEPTH_HINTS = [
    "깨달", "알게 되었", "인식했", "돌아보", "패턴", "반복", "습관",
    "다음에는", "다음엔", "앞으로는", "바꾸고 싶", "변화", "성장",
]

TOMORROW_ACTION_HINTS = [
    "하겠다", "해보자", "해보려", "해야겠다", "하기", "10분", "30분",
    "한 번", "한번", "정리", "연습", "적어보",
]

TOMORROW_VAGUE_ONLY = [
    "열심히 살자", "잘해보자", "잘 살아보자", "괜찮아질 거야",
]


# 모드 임계값들
SLUMP_EMOTION_THRESHOLD = -0.4
OVERLOAD_EMOTION_THRESHOLD = -0.3
GROWTH_INSIGHT_THRESHOLD = 0.4
GROWTH_TOMORROW_THRESHOLD = 0.3


# ================================
# 1. 내부에서 사용할 자료 구조
# ================================

@dataclass
class AnalysisScores:
    emotion: float          # -1.0 ~ 1.0
    event: float            # -1.0 ~ 1.0 (구체성 기준)
    reason: float           # -1.0 ~ 1.0 (논리성 / 일관성)
    insight: float          # -1.0 ~ 1.0 (깊이)
    tomorrow: float         # -1.0 ~ 1.0 (실행가능성)
    final: float            # -1.0 ~ 1.0 (종합 점수)


# ================================
# 2. 유틸 함수들
# ================================

def _normalize(text: Optional[str]) -> str:
    if not text:
        return ""
    # 공백 정리
    return re.sub(r"\s+", " ", text).strip()


def _length_score(text: str) -> float:
    """텍스트 길이에 따른 대략적인 정보량 점수 (0.0 ~ 1.0)"""
    n = len(text)
    if n == 0:
        return 0.0
    if n < 10:
        return 0.2
    if n < 30:
        return 0.5
    if n < 80:
        return 0.8
    return 1.0


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(p in text for p in patterns)


def _count_matches(text: str, patterns: list[str]) -> int:
    return sum(1 for p in patterns if p in text)


# ================================
# 3. 각 레이어별 점수 계산
# ================================

def _emotion_score(emotion: str) -> float:
    """감정 레이어 점수 (-1.0 ~ 1.0)"""
    t = _normalize(emotion)

    # 기본 점수 0
    score = 0.0

    neg_count = _count_matches(t, NEGATIVE_WORDS)
    pos_count = _count_matches(t, POSITIVE_WORDS)

    score += pos_count * 0.2
    score -= neg_count * 0.2

    if _contains_any(t, STRONG_POSITIVE_PATTERNS):
        score += 0.3
    if _contains_any(t, STRONG_NEGATIVE_PATTERNS):
        score -= 0.3

    # 클리핑
    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0

    # 아예 비어 있으면 아주 약한 중립
    if len(t) == 0:
        score = 0.0

    return score


def _event_score(event: str) -> float:
    """사건의 구체성 점수 (-1.0 ~ 1.0)"""
    t = _normalize(event)
    if not t:
        return -0.2

    words = t.split(" ")
    base = _length_score(t)

    concrete_hits = _count_matches(t, EVENT_CONCRETE_HINTS)
    score = base - 0.2  # 기본값을 약간 낮게 시작
    score += concrete_hits * 0.15

    if len(words) < 3:
        score -= 0.2  # 너무 짧으면 구체성 부족

    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return score


def _reason_score(emotion: str, event: str, reason: str) -> float:
    """이유의 논리성 / 일관성 점수 (-1.0 ~ 1.0)"""
    t = _normalize(reason)
    if not t:
        return -0.2

    base = _length_score(t)
    score = base - 0.2

    # 논리 접속어 있으면 플러스
    if _contains_any(t, REASON_LOGIC_WORDS):
        score += 0.3

    # 감정과 이유의 톤이 완전히 반대면 감점
    emo_score = _emotion_score(emotion)
    if emo_score > 0.4 and _contains_any(t, NEGATIVE_WORDS):
        score -= 0.3
    if emo_score < -0.4 and _contains_any(t, POSITIVE_WORDS):
        score -= 0.3

    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return score


def _insight_score(reason: str, insight: str) -> float:
    """인사이트 깊이 점수 (-1.0 ~ 1.0)"""
    t = _normalize(reason + " " + insight)
    if not t:
        return -0.3

    base = _length_score(t) - 0.2
    depth_hits = _count_matches(t, INSIGHT_DEPTH_HINTS)

    score = base + depth_hits * 0.2

    if "모르겠" in t:
        score -= 0.3

    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return score


def _tomorrow_score(tomorrow: str) -> float:
    """내일의 한 문장 실행 가능성 점수 (-1.0 ~ 1.0)"""
    t = _normalize(tomorrow)
    if not t:
        return -0.2

    base = _length_score(t) - 0.2
    score = base

    if _contains_any(t, TOMORROW_ACTION_HINTS):
        score += 0.3

    if _contains_any(t, TOMORROW_VAGUE_ONLY):
        score -= 0.2

    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return score


# ================================
# 4. 모호성 판정
# ================================

def _is_ambiguous(emotion: str, event: str, reason: str, insight: str, tomorrow: str) -> bool:
    all_text = _normalize(" ".join([emotion, event, reason, insight, tomorrow]))
    if len(all_text) < 10:
        return True

    core_filled = sum(
        1 for t in [emotion, event, reason] if t and len(t.strip()) >= 5
    )
    if core_filled == 0:
        return True

    return False


# ================================
# 5. 종합 분석 + 모드 판정
# ================================

def _compute_scores(
    emotion: str, event: str, reason: str, insight: str, tomorrow: str
) -> AnalysisScores:
    emo = _emotion_score(emotion)
    evt = _event_score(event)
    rsn = _reason_score(emotion, event, reason)
    ins = _insight_score(reason, insight)
    tmr = _tomorrow_score(tomorrow)

    final = (
        emo * 0.25 +
        evt * 0.20 +
        rsn * 0.15 +
        ins * 0.25 +
        tmr * 0.15
    )

    # 클리핑
    if final > 1.0:
        final = 1.0
    if final < -1.0:
        final = -1.0

    return AnalysisScores(
        emotion=emo,
        event=evt,
        reason=rsn,
        insight=ins,
        tomorrow=tmr,
        final=final,
    )


def _classify_mode(scores: AnalysisScores, is_ambiguous: bool) -> Dict[str, str]:
    if is_ambiguous:
        return {
            "mode": "ambiguous",
            "label": "모호 모드",
            "description": (
                "지금의 마음을 아직 말로 다 풀어내기 어려운 상태일 수 있어요. "
                "그럼에도 이렇게 한 줄이라도 남겨 둔 것이 이미 중요한 시작이에요."
            ),
        }

    emo = scores.emotion
    ins = scores.insight
    tmr = scores.tomorrow
    final = scores.final

    # 1) 슬럼프
    if emo < SLUMP_EMOTION_THRESHOLD and ins < 0:
        return {
            "mode": "slump",
            "label": "슬럼프 모드",
            "description": (
                "에너지가 많이 떨어져 있거나, 하고 싶은 마음이 잘 나지 않는 시기일 수 있어요. "
                "지금은 '해야 하는 나'보다 '있는 그대로의 나'를 허용해 주는 시간이 더 필요할 수 있어요."
            ),
        }

    # 2) 과부하
    if emo < OVERLOAD_EMOTION_THRESHOLD and scores.event < 0 and scores.reason < 0:
        return {
            "mode": "overload",
            "label": "정서적 과부하 모드",
            "description": (
                "머리와 마음이 동시에 과부하 상태에 가까운 듯 보여요. "
                "이럴 땐 할 일을 더 늘리기보다, 부담을 잠깐 내려놓고 숨을 고르는 시간이 아주 중요해요."
            ),
        }

    # 3) 성장
    if ins > GROWTH_INSIGHT_THRESHOLD or tmr > GROWTH_TOMORROW_THRESHOLD:
        return {
            "mode": "growth",
            "label": "성장 모드",
            "description": (
                "오늘의 경험을 단순한 사건으로 두지 않고, 나를 이해하고 다음을 준비하는 재료로 삼고 있어요. "
                "이런 시선 자체가 이미 큰 성장의 신호예요."
            ),
        }

    # 4) 루틴 (평범한 일상, 큰 기복 없음)
    if -0.2 <= scores.emotion <= 0.2 and -0.2 <= final <= 0.2:
        return {
            "mode": "routine",
            "label": "루틴 모드",
            "description": (
                "크게 흔들리지 않는 일상을 꾸준히 이어가고 있는 모습이에요. "
                "이런 평범한 날들이 나중에 돌아보면 튼튼한 바닥이 되어 줄 거예요."
            ),
        }

    # 5) 기본값: 안정/중립
    return {
        "mode": "stable",
        "label": "안정 모드",
        "description": (
            "극단적인 감정의 파도보다는, 나름의 리듬 속에서 하루를 정리하고 있는 모습이에요. "
            "이 흐름을 지키는 것만으로도 이미 잘 해내고 있어요."
        ),
    }


# ================================
# 6. 외부에서 쓰는 메인 함수들
# ================================

def analyze_entry(entry: Any) -> Dict[str, Any]:
    """
    SQLAlchemy 모델이든, Pydantic 모델이든
    emotion/event/reason/insight/tomorrow 속성만 있으면 동작하도록 설계.
    """
    emotion = getattr(entry, "emotion", "") or ""
    event = getattr(entry, "event", "") or ""
    reason = getattr(entry, "reason", "") or ""
    insight = getattr(entry, "insight", "") or ""
    tomorrow = getattr(entry, "tomorrow", "") or ""

    ambiguous = _is_ambiguous(emotion, event, reason, insight, tomorrow)
    scores = _compute_scores(emotion, event, reason, insight, tomorrow)
    mode_info = _classify_mode(scores, ambiguous)

    result: Dict[str, Any] = {
        "mode": mode_info["mode"],
        "modeLabel": mode_info["label"],
        "modeDescription": mode_info["description"],
        "scores": {
            "emotion": scores.emotion,
            "event": scores.event,
            "reason": scores.reason,
            "insight": scores.insight,
            "tomorrow": scores.tomorrow,
            "final": scores.final,
        },
        "isAmbiguous": ambiguous,
    }
    return result


def generate_coaching(entry: Any, analysis: Dict[str, Any]) -> str:
    """
    모드 + 점수 기반 코칭 메시지.
    나중에 톤, 길이, 조건은 여기서만 수정하면 됨.
    """
    mode = analysis.get("mode", "stable")
    is_ambiguous = analysis.get("isAmbiguous", False)

    if is_ambiguous or mode == "ambiguous":
        return (
            "지금은 마음을 딱 맞는 말로 표현하기가 쉽지 않을 수도 있어요. "
            "그래도 이렇게 화면을 열고 몇 글자라도 남긴 것 자체가 이미 중요한 한 걸음이에요. "
            "오늘은 '이런 마음이 있었구나' 하고 가볍게만 인정해 주어도 충분해요."
        )

    if mode == "slump":
        return (
            "요즘 에너지가 잘 나지 않거나, 사소한 일에도 쉽게 지칠 수 있는 시기일 거예요. "
            "이럴 때일수록 '이 정도면 이미 많이 하고 있다'는 시선으로 나를 바라봐 주는 게 중요해요. "
            "내일은 거창한 목표 대신, 물 한 컵 마시기 같은 아주 작은 행동 하나만 나를 위해 챙겨 보면 어떨까요?"
        )

    if mode == "overload":
        return (
            "지금은 머릿속과 마음이 동시에 과부하에 가까워 보이에요. "
            "해야 할 일을 한 번에 다 처리하려 하기보다는, 가장 부담이 적은 것 하나만 골라서 줄여 보는 것도 괜찮아요. "
            "오늘이나 내일 중에 5분이라도 '아무것도 하지 않는 시간'을 자신에게 허락해 줄 수 있을까요?"
        )

    if mode == "growth":
        return (
            "오늘의 경험을 통해 나를 이해하고, 다음을 준비하려는 태도가 잘 느껴져요. "
            "완벽하게 해내지 못한 순간조차도 다음을 위한 데이터로 바라보는 시선이 참 단단해 보여요. "
            "내일은 오늘 떠올린 생각들 중 가장 가벼운 것 하나만 골라 10초 정도 실천해 보는 것만으로도 충분해요."
        )

    if mode == "routine":
        return (
            "크게 특별한 사건은 없었을지 몰라도, 이런 일상을 기록해 두는 습관이 이미 큰 자산이에요. "
            "루틴은 눈에 띄는 성취보다 '지금의 나를 지켜 주는 힘'을 길러줘요. "
            "내일은 기존 루틴에 10초짜리 새로운 시도를 살짝 얹어 보는 정도만 해도 좋아요."
        )

    if mode == "stable":
        return (
            "오늘 하루를 비교적 차분하게 정리해 둔 모습에서, 스스로의 리듬을 잘 지키고 있는 인상이 느껴져요. "
            "이런 날들이 쌓일수록 감정의 큰 파도에도 덜 휩쓸리게 되는 경우가 많아요. "
            "내일은 이 안정감을 지켜 줄 수 있는 작은 습관 하나를 다시 한 번 떠올려 보면 좋겠어요."
        )

    # 예외적으로 모드가 예상 밖일 때
    return (
        "오늘 하루를 이렇게 글로 남겨 둔 것만으로도 이미 큰 수고를 한 거예요. "
        "지금의 감정을 있는 그대로 인정해 주는 것에서부터 다음 걸음이 시작돼요. "
        "내일의 나에게 건네고 싶은 한 문장을 마음속으로만 조용히 떠올려 보는 것도 좋은 마무리가 될 거예요."
    )

def analyze_mode(entry: Any) -> Dict[str, Any]:
    """
    이전 코드에서 사용하던 이름을 유지하기 위한 래퍼.
    내부적으로는 analyze_entry를 그대로 호출한다.
    """
    return analyze_entry(entry)

