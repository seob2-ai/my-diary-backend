# Phase 1 긴급 리팩토링 실행 계획

## 📋 개요

**목표**: 4가지 긴급 이슈를 안전하게 수정하여 런타임 에러 방지 및 보안 강화  
**예상 소요 시간**: 약 30-40분  
**위험도**: 낮음 (각 단계는 독립적이며 롤백 가능)

---

## 🔄 전체 프로세스 흐름

```
[사전 준비] → [Step 1] → [검증] → [Step 2] → [검증] → [Step 3] → [검증] → [Step 4] → [최종 검증]
```

---

## 📦 사전 준비 단계

### 1.1 현재 상태 백업
- [ ] Git 커밋 생성 (현재 상태 저장)
- [ ] 데이터베이스 백업 (선택사항, SQLite 파일 복사)

### 1.2 환경 확인
- [ ] 서버가 실행 중이면 중지
- [ ] 테스트 환경 준비 (로컬 개발 환경)

### 1.3 의존성 확인
```bash
# python-dotenv가 필요할 수 있음 (Step 4에서 사용)
pip list | grep python-dotenv
```

---

## 📝 Step 1: WeeklySummaryResponse 스키마 추가

### 목표
`app/schemas.py`에 누락된 `WeeklySummaryResponse` 스키마를 추가하여 런타임 에러 방지

### 위험도: ⭐ 매우 낮음
- 기존 코드에 영향 없음
- 단순 추가 작업
- 즉시 롤백 가능

### 실행 절차

#### 1.1 사전 검증
```python
# app/routers/summary.py를 확인하여 필요한 필드 파악
# 현재 사용 중인 필드:
# - startDate: date
# - endDate: date  
# - totalEntries: int
# - modeCounts: Dict[str, int]
# - highlights: Dict[str, Optional[str]]
```

#### 1.2 코드 수정
**파일**: `app/schemas.py`

**추가할 내용**:
```python
# ---------- Summary (응답용) ----------
class WeeklySummaryResponse(BaseModel):
    """
    주간 요약 응답 스키마
    """
    startDate: date
    endDate: date
    totalEntries: int
    modeCounts: Dict[str, int]
    highlights: Dict[str, Optional[str]]
```

**위치**: `DiaryAnalysisResult` 클래스 다음에 추가 (약 86번째 줄 이후)

#### 1.3 사후 검증
- [ ] Python 문법 검사: `python -m py_compile app/schemas.py`
- [ ] Import 테스트: `python -c "from app import schemas; print(schemas.WeeklySummaryResponse)"`
- [ ] 서버 시작 테스트: `uvicorn app.main:app --reload` (에러 없이 시작되는지 확인)

#### 1.4 롤백 방법
```bash
git checkout app/schemas.py
```

#### 1.5 예상 결과
- ✅ `app/routers/summary.py`에서 `schemas.WeeklySummaryResponse` 정상 import
- ✅ 서버 시작 시 에러 없음
- ✅ `/api/summary/weekly` 엔드포인트 정상 동작

---

## 📝 Step 2: parse_date_or_today 에러 처리 추가

### 목표
날짜 파싱 실패 시 명확한 에러 메시지와 함께 400 에러 반환

### 위험도: ⭐ 낮음
- 기존 정상 케이스에 영향 없음
- 에러 케이스만 개선
- 즉시 롤백 가능

### 실행 절차

#### 2.1 사전 검증
- [ ] 현재 `parse_date_or_today` 함수 사용 위치 확인
  - `app/routers/diary.py:40` (list_diaries)
  - `app/routers/diary.py:62` (create_diary)

#### 2.2 코드 수정
**파일**: `app/routers/diary.py`

**수정 전**:
```python
def parse_date_or_today(date_str: Optional[str]) -> date:
    if not date_str:
        return datetime.now().date()
    return datetime.strptime(date_str, "%Y-%m-%d").date()
```

**수정 후**:
```python
def parse_date_or_today(date_str: Optional[str]) -> date:
    """
    날짜 문자열을 date 객체로 변환. 없으면 오늘 날짜 반환.
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        
    Returns:
        date 객체
        
    Raises:
        HTTPException: 날짜 형식이 올바르지 않은 경우 (400)
    """
    if not date_str:
        return datetime.now().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요. (입력값: {date_str})"
        )
```

#### 2.3 사후 검증
- [ ] 정상 케이스 테스트:
  ```python
  # 테스트 1: None 입력 → 오늘 날짜 반환
  # 테스트 2: "2024-01-15" 입력 → date(2024, 1, 15) 반환
  ```
- [ ] 에러 케이스 테스트:
  ```python
  # 테스트 3: "2024-13-45" 입력 → HTTPException 발생 확인
  # 테스트 4: "invalid" 입력 → HTTPException 발생 확인
  ```
- [ ] API 테스트:
  ```bash
  # 정상 요청
  curl -X GET "http://localhost:8000/api/diary?date=2024-01-15" -H "x-user-id: test"
  
  # 에러 요청 (400 에러 확인)
  curl -X GET "http://localhost:8000/api/diary?date=invalid" -H "x-user-id: test"
  ```

#### 2.4 롤백 방법
```bash
git checkout app/routers/diary.py
```

#### 2.5 예상 결과
- ✅ 정상 날짜 입력 시 기존과 동일하게 동작
- ✅ 잘못된 날짜 입력 시 400 에러와 명확한 메시지 반환
- ✅ 기존 기능 영향 없음

---

## 📝 Step 3: 트랜잭션 롤백 처리 추가

### 목표
데이터베이스 작업 실패 시 자동 롤백으로 데이터 일관성 보장

### 위험도: ⭐⭐ 낮음-중간
- 기존 정상 케이스에 영향 없음
- 에러 처리 로직 추가
- 주의 깊게 테스트 필요

### 실행 절차

#### 3.1 사전 검증
- [ ] 현재 DB 작업 위치 확인:
  - `app/routers/diary.py:103-105` (create_diary)
  - 다른 DB 수정 작업이 있는지 확인

#### 3.2 코드 수정
**파일**: `app/routers/diary.py`

**수정 전**:
```python
db.add(db_diary)
db.commit()
db.refresh(db_diary)
return db_diary
```

**수정 후**:
```python
try:
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary
except Exception as e:
    db.rollback()
    # 로깅을 위한 에러 정보 (나중에 로깅 시스템 추가 시 활용)
    raise HTTPException(
        status_code=500,
        detail="일기 저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    )
```

#### 3.3 추가 고려사항
**다른 DB 수정 작업 확인**:
- `app/routers/diary.py`의 `create_diary`만 DB 수정 작업 수행
- 다른 라우터에서 DB 수정이 있다면 동일하게 적용

#### 3.4 사후 검증
- [ ] 정상 케이스 테스트:
  ```bash
  # 정상 일기 생성
  curl -X POST "http://localhost:8000/api/diary" \
    -H "x-user-id: test" \
    -H "Content-Type: application/json" \
    -d '{"emotion": "기쁨", "event": "테스트"}'
  ```
- [ ] 에러 케이스 테스트 (의도적 에러 발생):
  - DB 연결 끊기 (서버 재시작 중 요청)
  - 제약 조건 위반 (중복 ID 등)
- [ ] 롤백 확인:
  - 에러 발생 후 DB에 불완전한 데이터가 저장되지 않았는지 확인

#### 3.5 롤백 방법
```bash
git checkout app/routers/diary.py
```

#### 3.6 예상 결과
- ✅ 정상 케이스는 기존과 동일하게 동작
- ✅ 에러 발생 시 자동 롤백
- ✅ 사용자에게 명확한 에러 메시지 제공
- ✅ 데이터 일관성 보장

---

## 📝 Step 4: CORS 설정 환경 변수화 및 제한

### 목표
보안 강화를 위해 CORS 설정을 환경 변수로 관리하고 기본값 제한

### 위험도: ⭐⭐ 낮음-중간
- 환경 변수 파일 필요
- 기본값 변경으로 인한 영향 가능
- 주의 깊게 테스트 필요

### 실행 절차

#### 4.1 사전 준비
- [ ] `python-dotenv` 설치 확인
  ```bash
  pip install python-dotenv
  # 또는 requirements.txt에 추가
  ```

#### 4.2 환경 변수 파일 생성
**파일**: `.env.example` (새로 생성)
```
# CORS 설정
# 개발 환경: http://localhost:3000,http://localhost:8080
# 프로덕션: 실제 도메인을 콤마로 구분하여 입력
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

**파일**: `.env` (로컬 개발용, .gitignore에 추가)
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### 4.3 .gitignore 확인
- [ ] `.env` 파일이 `.gitignore`에 있는지 확인
- [ ] 없으면 추가

#### 4.4 코드 수정
**파일**: `app/main.py`

**수정 전**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**수정 후**:
```python
import os
from typing import List

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# CORS 허용 출처 설정
ALLOWED_ORIGINS_STR = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080"  # 기본값: 개발 환경
)
ALLOWED_ORIGINS: List[str] = [
    origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 환경 변수에서 읽은 출처 목록
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 필요한 메서드만 명시
    allow_headers=["*"],
)
```

#### 4.5 requirements.txt 업데이트
**파일**: `app/requirements.txt`

**추가**:
```
python-dotenv>=1.0.0
```

#### 4.6 사후 검증
- [ ] 환경 변수 로드 확인:
  ```python
  # Python 콘솔에서 테스트
  from dotenv import load_dotenv
  import os
  load_dotenv()
  print(os.getenv("ALLOWED_ORIGINS"))
  ```
- [ ] CORS 동작 테스트:
  ```bash
  # 허용된 출처에서 요청 (정상 동작)
  curl -X GET "http://localhost:8000/api/diary" \
    -H "x-user-id: test" \
    -H "Origin: http://localhost:3000"
  
  # 차단된 출처에서 요청 (CORS 에러 확인)
  curl -X GET "http://localhost:8000/api/diary" \
    -H "x-user-id: test" \
    -H "Origin: http://malicious-site.com"
  ```
- [ ] 기본값 동작 확인:
  - `.env` 파일 없이 서버 시작 시 기본값 사용 확인

#### 4.7 롤백 방법
```bash
git checkout app/main.py
rm .env .env.example  # 필요시
```

#### 4.8 예상 결과
- ✅ 환경 변수로 CORS 설정 관리 가능
- ✅ 기본값은 개발 환경에 맞게 제한됨
- ✅ 프로덕션 환경에서 실제 도메인만 허용 가능
- ✅ 보안 강화

---

## ✅ 최종 검증 단계

### 전체 기능 테스트

#### 1. 서버 시작 확인
```bash
uvicorn app.main:app --reload
# 에러 없이 시작되는지 확인
```

#### 2. API 엔드포인트 테스트

**2.1 일기 생성 (POST /api/diary)**
```bash
curl -X POST "http://localhost:8000/api/diary" \
  -H "x-user-id: test-user" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "emotion": "기쁨",
    "event": "테스트 이벤트",
    "reason": "테스트 이유",
    "insight": "테스트 인사이트",
    "tomorrow": "테스트 내일"
  }'
```

**2.2 일기 목록 조회 (GET /api/diary)**
```bash
curl -X GET "http://localhost:8000/api/diary?date=2024-01-15" \
  -H "x-user-id: test-user"
```

**2.3 잘못된 날짜 형식 테스트 (400 에러 확인)**
```bash
curl -X GET "http://localhost:8000/api/diary?date=invalid-date" \
  -H "x-user-id: test-user"
```

**2.4 주간 요약 조회 (GET /api/summary/weekly)**
```bash
curl -X GET "http://localhost:8000/api/summary/weekly" \
  -H "x-user-id: test-user"
```

#### 3. 에러 처리 확인
- [ ] 날짜 파싱 에러 시 400 에러 반환 확인
- [ ] DB 에러 시 롤백 및 500 에러 반환 확인
- [ ] CORS 차단 동작 확인

#### 4. 코드 품질 확인
- [ ] Python 문법 검사: `python -m py_compile app/**/*.py`
- [ ] Import 검사: 모든 모듈 정상 import 확인

---

## 🔄 롤백 계획

### 전체 롤백
```bash
# 모든 변경사항 취소
git reset --hard HEAD

# 또는 특정 커밋으로 되돌리기
git reset --hard <commit-hash>
```

### 부분 롤백
각 Step의 롤백 방법 참조

---

## 📊 진행 상황 체크리스트

### 사전 준비
- [ ] Git 커밋 생성
- [ ] 서버 중지
- [ ] 의존성 확인

### Step 1: 스키마 추가
- [ ] 코드 수정
- [ ] 검증 완료
- [ ] 문제 없음 확인

### Step 2: 날짜 파싱 에러 처리
- [ ] 코드 수정
- [ ] 검증 완료
- [ ] 문제 없음 확인

### Step 3: 트랜잭션 롤백
- [ ] 코드 수정
- [ ] 검증 완료
- [ ] 문제 없음 확인

### Step 4: CORS 설정
- [ ] 환경 변수 파일 생성
- [ ] 코드 수정
- [ ] 검증 완료
- [ ] 문제 없음 확인

### 최종 검증
- [ ] 전체 기능 테스트 완료
- [ ] 에러 처리 확인 완료
- [ ] 코드 품질 확인 완료

---

## ⚠️ 주의사항

1. **순차적 진행**: 각 Step을 순서대로 진행하고 검증 완료 후 다음 단계로 진행
2. **테스트 필수**: 각 Step마다 반드시 테스트 수행
3. **롤백 준비**: 문제 발생 시 즉시 롤백 가능하도록 Git 상태 확인
4. **환경 변수**: Step 4에서 `.env` 파일을 생성했는지 확인
5. **의존성**: `python-dotenv` 설치 확인

---

## 🎯 성공 기준

- ✅ 모든 API 엔드포인트 정상 동작
- ✅ 에러 처리 개선 (날짜 파싱, DB 트랜잭션)
- ✅ CORS 설정 환경 변수화 완료
- ✅ 런타임 에러 없음
- ✅ 기존 기능 영향 없음

---

## 📝 완료 후 작업

1. **Git 커밋**
   ```bash
   git add .
   git commit -m "refactor: Phase 1 긴급 리팩토링 완료
   
   - WeeklySummaryResponse 스키마 추가
   - 날짜 파싱 에러 처리 개선
   - 트랜잭션 롤백 처리 추가
   - CORS 설정 환경 변수화"
   ```

2. **문서 업데이트**
   - `.env.example` 파일을 README에 설명 추가
   - 환경 변수 설정 방법 문서화

3. **다음 단계 준비**
   - Phase 2 리팩토링 계획 검토



