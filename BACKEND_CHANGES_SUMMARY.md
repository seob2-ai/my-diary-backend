# 백엔드 변경사항 요약

## 최근 변경사항 (검색 기능 개선)

### 1. 검색 API 개선 (`app/routers/diary.py`)

**변경 내용:**
- 검색 API에 `coaching` 필드 추가
- `or_` 함수를 SQLAlchemy에서 import 추가
- NULL 값 처리 개선 (coaching 필드)

**변경 전:**
```python
# emotion, event, reason, insight, tomorrow 필드만 검색
models.DiaryEntry.emotion.ilike(search_term) |
models.DiaryEntry.event.ilike(search_term) |
...
```

**변경 후:**
```python
# coaching 필드 추가
from sqlalchemy import func, or_

search_conditions = [
    models.DiaryEntry.emotion.ilike(search_term),
    models.DiaryEntry.event.ilike(search_term),
    models.DiaryEntry.reason.ilike(search_term),
    models.DiaryEntry.insight.ilike(search_term),
    models.DiaryEntry.tomorrow.ilike(search_term),
]

# coaching 필드는 NULL이 아닐 때만 검색
search_conditions.append(
    (models.DiaryEntry.coaching.isnot(None)) & 
    (models.DiaryEntry.coaching.ilike(search_term))
)

results = db.query(models.DiaryEntry)
    .filter(models.DiaryEntry.user_id == user_id)
    .filter(or_(*search_conditions))
    ...
```

**영향:**
- 검색 API가 `coaching` 필드까지 검색하도록 개선
- "AI" 같은 단어가 coaching 필드에 있어도 검색 가능

### 2. 데이터베이스 초기화 스크립트 추가 (`init_db.py`)

**목적:**
- 데이터베이스 테이블이 없을 경우 수동으로 생성할 수 있는 스크립트

**사용법:**
```bash
python init_db.py
```

**기능:**
- `diary_entries` 테이블 생성
- 생성된 테이블 목록 확인

## 테스트 상태

- ✅ 데이터베이스 테이블 생성 완료
- ✅ 검색 API 코드 수정 완료
- ⚠️ 백엔드 서버 재시작 필요 (변경사항 적용)

## 다음 단계

1. **백엔드 서버 재시작:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8016
   ```

2. **검색 기능 테스트:**
   - "AI" 키워드로 검색 테스트
   - coaching 필드에 포함된 단어 검색 테스트

3. **변경사항 커밋 (선택사항):**
   ```bash
   git add app/routers/diary.py init_db.py
   git commit -m "feat: 검색 API에 coaching 필드 추가 및 DB 초기화 스크립트 추가"
   ```

