# PRD 기반 추가 기능 제안서

## 📊 현재 구현 상태 (2024)

### ✅ 완료된 핵심 기능
1. **일기 CRUD** - 생성, 조회, 수정, 삭제
2. **일기 검색** - 텍스트 기반 검색
3. **일기 통계** - 전체/월별/주별 통계
4. **분석 기능** - 모드 분석, 모호성 판단
5. **코칭 메시지** - 자동 코칭 생성 및 저장
6. **분석 미리보기** - 저장 전 분석 결과 확인
7. **주간 요약** - 주간 일기 요약 및 하이라이트
8. **월간 요약** - 월간 통계 및 트렌드

---

## 🎯 PRD 기반 추가 기능 제안

### 🔴 **Phase 1: 핵심 가치 강화 기능 (우선순위 높음)**

#### 1.1 감정 트렌드 분석 API
**PRD 목적**: 감정 변화 추적은 "자아성찰" 앱의 핵심 가치  
**비즈니스 가치**: 사용자가 자신의 감정 패턴을 시각화하고 이해할 수 있음

**기능 상세**:
```
GET /api/analytics/emotion-trends
Query Parameters:
  - start_date: YYYY-MM-DD (선택, 기본값: 30일 전)
  - end_date: YYYY-MM-DD (선택, 기본값: 오늘)
  - granularity: day|week|month (기본값: day)

Response:
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "granularity": "day"
  },
  "emotion_distribution": {
    "positive": 15,
    "neutral": 10,
    "negative": 5
  },
  "daily_trends": [
    {
      "date": "2024-01-01",
      "emotion_score": 0.7,  // -1.0 ~ 1.0 (긍정적일수록 높음)
      "dominant_emotion": "기쁨",
      "entry_count": 1
    }
  ],
  "insights": [
    "이번 달 긍정적 감정이 50% 증가했습니다",
    "화요일에 감정 점수가 가장 높습니다"
  ]
}
```

**예상 소요 시간**: 4-6시간  
**기술 요구사항**:
- 감정 키워드 매핑 로직 (간단한 NLP 또는 키워드 기반)
- 시계열 데이터 집계
- 통계 분석 로직

---

#### 1.2 일기 작성 연속성 추적 (Streak)
**PRD 목적**: 꾸준한 습관 형성 지원, 게이미피케이션 요소  
**비즈니스 가치**: 사용자 참여도 및 리텐션 향상

**기능 상세**:
```
GET /api/analytics/streak

Response:
{
  "current_streak": 7,  // 연속 작성 일수
  "longest_streak": 21,
  "total_days": 45,  // 총 작성 일수
  "calendar_data": {
    "2024-01-01": true,  // 작성했는지 여부
    "2024-01-02": true,
    "2024-01-03": false
  },
  "weekly_goal": 7,  // 주간 목표
  "weekly_progress": 5,  // 이번 주 작성 수
  "achievement_badges": [
    "first_week",  // 첫 주 완성
    "one_month"    // 한 달 완성
  ]
}
```

**예상 소요 시간**: 3-4시간  
**추가 고려사항**:
- 목표 설정 API 필요
- 배지 시스템 확장 가능

---

#### 1.3 고급 필터링 및 정렬
**PRD 목적**: 많은 일기 중 원하는 내용을 쉽게 찾기  
**비즈니스 가치**: 사용자 경험 향상, 일기 활용도 증가

**기능 상세**:
```
GET /api/diary
Query Parameters (기존 + 추가):
  - mode: ACTIONABLE|REFLECTION|EMOTION_DUMP 등 (필터링)
  - start_date: YYYY-MM-DD (범위 시작)
  - end_date: YYYY-MM-DD (범위 끝)
  - emotion_keyword: string (감정 키워드 필터)
  - min_length: int (최소 글자 수)
  - max_length: int (최대 글자 수)
  - sort: date_asc|date_desc|length_asc|length_desc|recent (기본값: recent)
  - has_coaching: bool (코칭 메시지 있는 일기만)
```

**예상 소요 시간**: 2-3시간

---

### 🟡 **Phase 2: 데이터 인사이트 강화 (중간 우선순위)**

#### 2.1 성장 지표 대시보드
**PRD 목적**: 장기적인 성찰의 가치 시각화  
**비즈니스 가치**: 사용자가 자신의 성장을 인지할 수 있게 함

**기능 상세**:
```
GET /api/analytics/growth-metrics
Query Parameters:
  - period: 30|90|180|365 (일수, 기본값: 30)

Response:
{
  "period_days": 30,
  "writing_consistency": {
    "avg_entries_per_week": 4.5,
    "consistency_score": 0.85,  // 0.0 ~ 1.0
    "trend": "increasing"  // increasing|stable|decreasing
  },
  "reflection_depth": {
    "avg_entry_length": 245,
    "deep_reflection_ratio": 0.35,  // REFLECTION_DEEP 비율
    "trend": "increasing"
  },
  "emotional_wellbeing": {
    "avg_emotion_score": 0.65,
    "volatility": 0.15,  // 감정 변동성 (낮을수록 안정적)
    "trend": "improving"
  },
  "actionability": {
    "actionable_entries_ratio": 0.42,
    "trend": "increasing"
  },
  "overall_growth_score": 72,  // 0-100
  "key_insights": [
    "지난 달보다 성찰 깊이가 20% 향상되었습니다",
    "긍정적 감정 비율이 증가했습니다"
  ]
}
```

**예상 소요 시간**: 6-8시간

---

#### 2.2 일기 태그 시스템
**PRD 목적**: 일기를 주제별로 분류하여 관리  
**비즈니스 가치**: 사용자가 일기를 더 체계적으로 관리

**기능 상세**:
```
# 스키마 추가
class DiaryEntry:
    tags: List[str] = []  # 예: ["감사", "성장", "관계", "업무"]

# API
POST /api/diary/{diary_id}/tags
Body: { "tags": ["감사", "성장"] }

GET /api/diary?tags=감사,성장  # 태그로 필터링

GET /api/analytics/tags
Response: {
  "tag_frequency": {
    "감사": 12,
    "성장": 8,
    "관계": 5
  },
  "tag_cooccurrence": {  // 함께 나타나는 태그
    "감사": ["성장", "관계"],
    "성장": ["감사"]
  }
}
```

**예상 소요 시간**: 4-5시간  
**데이터베이스 변경 필요**: tags 컬럼 추가 또는 별도 태그 테이블

---

#### 2.3 월별/연도별 리포트 생성
**PRD 목적**: 장기적인 성찰 결과를 요약하여 제공  
**비즈니스 가치**: 사용자가 큰 그림을 볼 수 있게 함

**기능 상세**:
```
GET /api/reports/monthly
Query Parameters:
  - year: int
  - month: int

Response:
{
  "period": "2024-01",
  "summary": {
    "total_entries": 28,
    "total_words": 6845,
    "most_frequent_mode": "REFLECTION_DEEP",
    "most_active_day": "2024-01-15"
  },
  "emotional_journey": {
    "start_emotion_score": 0.5,
    "end_emotion_score": 0.7,
    "peak_day": "2024-01-20",
    "low_day": "2024-01-05"
  },
  "top_insights": [
    "이번 달 가장 많이 다룬 주제: 관계",
    "주말에 더 깊은 성찰을 하는 경향이 있습니다"
  ],
  "recommendations": [
    "다음 달에는 ACTIONABLE 모드로 전환해보세요",
    "화요일 저녁에 일기 작성하는 것을 추천합니다"
  ]
}
```

**예상 소요 시간**: 5-6시간

---

### 🟢 **Phase 3: 고급 기능 및 통합 (장기)**

#### 3.1 일기 내보내기 (Export)
**PRD 목적**: 사용자 데이터 소유권 보장, 백업 기능  
**비즈니스 가치**: 사용자 신뢰도 향상

**기능 상세**:
```
GET /api/export/diary
Query Parameters:
  - format: json|csv|pdf|markdown (기본값: json)
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD

Response:
- JSON/CSV: 직접 다운로드
- PDF/Markdown: 파일 생성 후 다운로드 링크 제공
```

**예상 소요 시간**: 3-4시간  
**추가 라이브러리**: 
- PDF: `reportlab` 또는 `weasyprint`
- Markdown: 내장 라이브러리 사용

---

#### 3.2 일기 템플릿 시스템
**PRD 목적**: 사용자가 일기를 더 쉽게 시작할 수 있도록 지원  
**비즈니스 가치**: 진입 장벽 낮추기, 일기 품질 향상

**기능 상세**:
```
# 모델 추가
class DiaryTemplate(Base):
    id: str
    name: str
    description: str
    prompt_fields: List[str]  # ["emotion", "event", "reason"]
    example_content: Dict[str, str]

# API
GET /api/templates
GET /api/templates/{template_id}
POST /api/diary?template_id=xxx  # 템플릿 기반 일기 생성
```

**예상 소요 시간**: 4-5시간  
**템플릿 예시**:
- "감사 일기" 템플릿
- "성장 성찰" 템플릿
- "감정 정리" 템플릿
- "내일 계획" 템플릿

---

#### 3.3 목표 설정 및 추적
**PRD 목적**: 사용자가 명확한 목표를 가지고 일기를 작성하도록 동기 부여  
**비즈니스 가치**: 참여도 및 목표 달성감 제공

**기능 상세**:
```
# 모델 추가
class Goal(Base):
    id: str
    user_id: str
    title: str
    description: str
    target_date: date
    status: active|completed|archived
    created_at: datetime

# API
POST /api/goals
GET /api/goals
PATCH /api/goals/{goal_id}
DELETE /api/goals/{goal_id}

# 일기와 목표 연결
POST /api/diary?goal_id=xxx

# 목표 진행도 조회
GET /api/goals/{goal_id}/progress
```

**예상 소요 시간**: 6-8시간

---

#### 3.4 AI 기반 개인화 코칭 (LLM 통합)
**PRD 목적**: 더 깊고 개인화된 코칭 제공  
**비즈니스 가치**: 프리미엄 기능으로 차별화

**기능 상세**:
```
# 기존 generate_coaching 함수 개선
- OpenAI/Claude API 통합
- 사용자의 과거 일기 히스토리 분석
- 개인화된 피드백 생성

POST /api/coaching/enhanced
Body: {
  "diary_id": "xxx",
  "include_history": true,  // 과거 일기 포함 여부
  "style": "gentle|direct|motivational"
}
```

**예상 소요 시간**: 2-3일  
**비용 고려사항**: API 호출 비용, 토큰 사용량  
**옵션**: 프리미엄 유저에게만 제공

---

#### 3.5 일기 공유 기능 (익명)
**PRD 목적**: 커뮤니티 형성, 영감 제공 (선택적)  
**비즈니스 가치**: 사용자 참여도 증가, 바이럴 확산 가능

**기능 상세**:
```
# 모델 추가
class SharedDiary(Base):
    id: str
    original_diary_id: str
    user_id: str
    shared_at: datetime
    view_count: int
    like_count: int
    is_anonymous: bool

# API
POST /api/diary/{diary_id}/share
GET /api/shared/diaries
POST /api/shared/{shared_id}/like
```

**예상 소요 시간**: 5-6시간  
**주의사항**: 프라이버시 고려, 익명화 처리 필요

---

### 🔵 **Phase 4: 기술적 개선 및 인프라**

#### 4.1 알림 시스템 (리마인더)
**PRD 목적**: 사용자가 꾸준히 일기를 작성하도록 리마인드  
**비즈니스 가치**: 리텐션 향상

**기능 상세**:
```
# 모델 추가
class NotificationPreference(Base):
    user_id: str
    reminder_enabled: bool
    reminder_time: time  # 예: "21:00"
    reminder_days: List[int]  # 0=월요일, 6=일요일

# API
GET /api/notifications/preferences
PATCH /api/notifications/preferences
```

**예상 소요 시간**: 4-5시간  
**추가 요구사항**: 
- 별도 워커 서비스 또는 스케줄러 필요
- 이메일/SMS/Push 알림 통합 (선택적)

---

#### 4.2 데이터 백업 및 복원
**PRD 목적**: 데이터 손실 방지  
**비즈니스 가치**: 신뢰도 향상

**기능 상세**:
```
POST /api/backup/create  # 수동 백업 생성
GET /api/backup/list
POST /api/backup/{backup_id}/restore
```

**예상 소요 시간**: 3-4시간  
**추가 고려사항**: 클라우드 스토리지 통합 (S3, GCS 등)

---

#### 4.3 다국어 지원 (i18n)
**PRD 목적**: 글로벌 사용자 확대  
**비즈니스 가치**: 시장 확장

**기능 상세**:
```
# API 응답에 언어 코드 추가
GET /api/diary?lang=ko|en|ja

# 코칭 메시지, 모드 설명 등을 다국어로 제공
```

**예상 소요 시간**: 5-6시간  
**추가 고려사항**: 번역 파일 관리, 번역 품질

---

## 📋 개발 우선순위 정리

### 즉시 시작 (1-2주 내)
1. ✅ **감정 트렌드 분석** - 핵심 가치 강화
2. ✅ **일기 작성 연속성 추적** - 게이미피케이션, 참여도 향상
3. ✅ **고급 필터링 및 정렬** - UX 개선

### 단기 계획 (1개월 내)
4. 성장 지표 대시보드
5. 일기 태그 시스템
6. 월별 리포트 생성

### 중기 계획 (2-3개월 내)
7. 일기 내보내기
8. 일기 템플릿 시스템
9. 목표 설정 및 추적

### 장기 계획 (3개월+)
10. AI 기반 개인화 코칭
11. 일기 공유 기능 (선택적)
12. 알림 시스템
13. 데이터 백업/복원
14. 다국어 지원

---

## 💡 추가 제안

### A/B 테스트 고려 기능
- 코칭 메시지 스타일 (gentle vs direct)
- 목표 설정 유무에 따른 참여도 차이
- 템플릿 제공 유무에 따른 일기 품질

### 데이터 분석 기능
- 사용자 행동 패턴 분석 (백엔드 로그 기반)
- 인기 태그/키워드 분석
- 코칭 메시지 효과 측정

### 보안 및 프라이버시 강화
- 일기 암호화 (선택적)
- 2단계 인증
- GDPR 준수 (데이터 삭제 요청 처리)

---

## 🎯 결론

**가장 우선적으로 구현할 기능 TOP 3**:
1. **감정 트렌드 분석** - 자아성찰 앱의 핵심 가치
2. **일기 작성 연속성 추적** - 사용자 참여도 및 리텐션
3. **고급 필터링 및 정렬** - 사용자 경험 개선

이 세 가지를 완료하면 "갓생·자아성찰 일기 앱"이 더욱 완성도 높은 서비스가 됩니다!


