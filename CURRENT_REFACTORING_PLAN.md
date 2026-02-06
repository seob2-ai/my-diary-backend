# 현재 진행 상황 기준 리팩토링 계획서

## 📊 현재 구현 상태 (2024-01-08)

### ✅ 완료된 기능
1. 일기 CRUD (생성, 조회, 수정, 삭제)
2. 일기 검색 및 통계
3. 주간/월간 요약
4. 감정 트렌드 분석 API
5. 일기 작성 연속성 추적 (Streak)
6. 분석 미리보기
7. 코칭 메시지 통합

### 📈 코드 통계
- 총 테스트: 43개 (모두 통과)
- 코드 커버리지: 77%
- 주요 파일:
  - `app/routers/analytics.py`: 146줄 (94% 커버리지)
  - `app/routers/diary.py`: 206줄 (55% 커버리지)
  - `app/routers/summary.py`: 85줄 (92% 커버리지)

---

## 🔴 긴급 리팩토링 사항 (우선순위 높음)

### 1. 날짜 파싱 로직 중복 제거
**위치**: `app/routers/analytics.py:63-90`  
**문제**: 날짜 파싱 로직이 중복되고, `parse_date_or_today`와 다른 패턴 사용  
**영향**: 유지보수 어려움, 일관성 부족

**현재 코드**:
```python
if end_date:
    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(...)
```

**개선 방안**:
- `utils.py`에 `parse_date_range()` 함수 추가
- 날짜 범위 검증 로직 통합

---

### 2. Granularity별 집계 로직 중복 및 복잡성
**위치**: `app/routers/analytics.py:141-262`  
**문제**: day/week/month 집계 로직이 매우 길고 중복 패턴이 많음 (약 120줄)  
**영향**: 가독성 저하, 버그 발생 가능성, 유지보수 어려움

**현재 구조**:
```python
if granularity == "day":
    # 20줄 코드
elif granularity == "week":
    # 40줄 코드
else:  # month
    # 50줄 코드
```

**개선 방안**:
- `emotion_service.py`에 집계 함수 분리
- 전략 패턴 또는 함수 매핑 사용
- 공통 로직 추출

---

### 3. 에러 핸들링 패턴 불일치
**위치**: 모든 라우터  
**문제**: 
- 일부는 `try-except HTTPException` 패턴
- 일부는 `except Exception`만 사용
- 일부는 중첩 try-except 사용

**영향**: 일관성 부족, 에러 처리 예측 어려움

**개선 방안**:
- 공통 에러 핸들러 데코레이터 생성
- 일관된 에러 처리 패턴 적용

---

### 4. 빈 데이터 처리 로직 중복
**위치**: `analytics.py`, `summary.py`  
**문제**: 빈 일기 리스트 처리 로직이 여러 곳에 중복  
**영향**: 코드 중복

**현재 코드**:
```python
if not entries:
    return schemas.EmotionTrendsResponse(...)  # 빈 응답
```

**개선 방안**:
- 공통 헬퍼 함수 생성

---

### 5. 감정 분포 계산 로직 중복
**위치**: `app/routers/analytics.py:131-138`  
**문제**: 감정 분포 카운트 로직이 인라인으로 구현됨  
**영향**: 재사용 어려움

**개선 방안**:
- `emotion_service.py`에 `calculate_emotion_distribution()` 함수 추가

---

## 🟡 중간 우선순위 리팩토링

### 6. 타입 힌팅 보완
**위치**: 여러 파일  
**문제**:
- `analytics.py`의 `daily_data: Dict[date, List[float]]` 등 일부만 타입 힌팅
- 함수 반환 타입이 명시되지 않은 경우 있음

**개선 방안**:
- 모든 함수에 타입 힌팅 추가
- `from __future__ import annotations` 사용 고려

---

### 7. 로깅 패턴 통일
**위치**: 모든 라우터  
**문제**:
- 로그 메시지 형식이 일관되지 않음
- 일부는 `logger.info`, 일부는 `logger.debug` 사용

**개선 방안**:
- 로깅 헬퍼 함수 생성
- 로그 메시지 템플릿 정의

---

### 8. 쿼리 최적화
**위치**: `analytics.py`, `streak.py`  
**문제**:
- `analytics.py`에서 이전 기간 조회를 위해 추가 쿼리 실행
- `streak.py`에서 모든 일기를 조회 후 메모리에서 처리

**개선 방안**:
- 필요한 데이터만 조회하도록 쿼리 최적화
- 인덱스 확인 및 추가

---

### 9. 상수 정의 통합
**위치**: 여러 파일  
**문제**:
- `emotion_service.py`에 키워드가 하드코딩
- `streak_service.py`에 매직 넘버 (7, 30, 100 등)

**개선 방안**:
- `constants.py`에 상수 통합
- 설정 가능한 값으로 변경

---

### 10. 테스트 커버리지 개선
**현재 상태**:
- `diary.py`: 55% (낮음)
- `summary.py`: 92% (양호)
- `analytics.py`: 94% (양호)

**개선 방안**:
- `diary.py`의 에러 케이스 테스트 추가
- 엣지 케이스 테스트 보완

---

## 🟢 낮은 우선순위 리팩토링

### 11. 함수 길이 최적화
**위치**: `app/routers/analytics.py:get_emotion_trends()`  
**문제**: 함수가 260줄 이상으로 매우 김  
**개선 방안**: 
- 날짜 파싱 → 별도 함수
- 집계 로직 → 별도 함수
- 트렌드 계산 → 별도 함수

---

### 12. 문서화 보완
**위치**: 모든 서비스 파일  
**문제**: 일부 함수에 docstring이 부족하거나 간단함  
**개선 방안**: 
- 모든 공개 함수에 상세 docstring 추가
- 예시 코드 포함

---

### 13. 성능 최적화
**위치**: `analytics.py`  
**문제**:
- 리스트 컴프리헨션 중복 사용
- 불필요한 반복 계산

**개선 방안**:
- 계산 결과 캐싱
- 불필요한 반복 제거

---

## 📋 우선순위별 실행 계획

### Phase 1: 긴급 (즉시 진행)
1. ✅ 날짜 파싱 로직 통합 (`parse_date_range` 함수)
2. ✅ Granularity 집계 로직 리팩토링 (함수 분리)
3. ✅ 감정 분포 계산 함수 추출

### Phase 2: 중간 (1주일 내)
4. 에러 핸들링 패턴 통일
5. 빈 데이터 처리 로직 통합
6. 타입 힌팅 보완
7. 로깅 패턴 통일

### Phase 3: 점진적 개선 (1개월 내)
8. 쿼리 최적화
9. 상수 정의 통합
10. 테스트 커버리지 개선
11. 함수 길이 최적화

---

## 🎯 예상 효과

### 코드 품질
- 중복 코드 제거: 약 100-150줄 감소 예상
- 가독성 향상: 함수 분리로 복잡도 감소
- 유지보수성 향상: 일관된 패턴 적용

### 성능
- 쿼리 최적화로 응답 시간 개선
- 불필요한 계산 제거

### 안정성
- 에러 핸들링 통일로 예외 처리 개선
- 테스트 커버리지 향상으로 버그 감소

---

## 💡 구체적 개선 예시

### 예시 1: 날짜 파싱 통합

**Before**:
```python
if end_date:
    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(...)
```

**After**:
```python
from app.utils import parse_date_range

start, end = parse_date_range(start_date, end_date, default_days=30)
```

### 예시 2: Granularity 집계 분리

**Before**: 120줄의 if-elif-else 블록

**After**:
```python
from app.services.emotion_service import aggregate_by_granularity

daily_trends = aggregate_by_granularity(
    entries, daily_data, start, end, granularity
)
```

---

## 📝 다음 단계

어떤 부분부터 리팩토링을 진행할까요?

1. **날짜 파싱 통합** (가장 빠르고 영향도 높음)
2. **Granularity 집계 리팩토링** (가장 큰 개선 효과)
3. **에러 핸들링 통일** (안정성 향상)


