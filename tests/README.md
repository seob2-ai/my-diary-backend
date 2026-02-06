# 테스트 가이드

## 테스트 환경 설정

### 1. 의존성 설치

```bash
# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 테스트 의존성 설치
pip install -r app/requirements.txt
```

### 2. 테스트 실행

#### 기본 테스트 실행
```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_diary_api.py

# 특정 테스트 클래스 실행
pytest tests/test_diary_api.py::TestDiaryAPI

# 특정 테스트 함수 실행
pytest tests/test_diary_api.py::TestDiaryAPI::test_create_diary

# 상세 출력
pytest -v
```

#### HTML 리포트 생성 (브라우저에서 확인)
```bash
# Windows
run_tests_with_report.bat

# Linux/Mac
./run_tests_with_report.sh

# 또는 직접 실행
pytest tests/ -v
```

테스트 실행 후 다음 파일을 브라우저에서 열 수 있습니다:
- `reports/report.html` - 테스트 결과 리포트
- `reports/coverage/index.html` - 코드 커버리지 리포트

#### 리포트 열기
```bash
# Windows
open_reports.bat

# Linux/Mac
./open_reports.sh
```

### 3. 테스트 마커 사용

```bash
# API 테스트만 실행
pytest -m api

# 단위 테스트만 실행
pytest -m unit

# 통합 테스트만 실행
pytest -m integration
```

## 테스트 구조

```
tests/
├── __init__.py              # 패키지 초기화
├── conftest.py              # pytest 설정 및 픽스처
├── test_diary_api.py        # 일기 API 테스트
├── test_summary_api.py      # 요약 API 테스트 (주간/월간)
├── test_analysis_service.py  # 분석 서비스 테스트
└── test_diary_preview.py    # 일기 미리보기 테스트
```

## 테스트 픽스처

- `test_db`: 테스트용 데이터베이스 세션 (각 테스트마다 새로 생성)
- `client`: FastAPI 테스트 클라이언트
- `test_user_id`: 테스트용 사용자 ID
- `sample_diary_data`: 샘플 일기 데이터
- `sample_diary_data_full`: 완전한 샘플 일기 데이터

## 테스트 작성 가이드

### 새로운 테스트 추가하기

1. 적절한 테스트 파일 선택 또는 새로 생성
2. 테스트 클래스 작성 (선택사항)
3. `@pytest.mark.api`, `@pytest.mark.unit` 등 마커 추가
4. 픽스처 활용하여 테스트 작성

예시:
```python
@pytest.mark.api
def test_my_new_feature(client, test_user_id):
    response = client.get("/api/my-endpoint", headers={"x-user-id": test_user_id})
    assert response.status_code == 200
```

## 리포트 확인

### HTML 테스트 리포트
- **위치**: `reports/report.html`
- **내용**: 
  - 테스트 실행 결과 (성공/실패)
  - 실행 시간
  - 에러 메시지 및 스택 트레이스
  - 테스트 통계

### 코드 커버리지 리포트
- **위치**: `reports/coverage/index.html`
- **내용**:
  - 코드 커버리지 퍼센트
  - 파일별 커버리지 상세 정보
  - 미커버된 라인 표시

## 주의사항

- 각 테스트는 독립적으로 실행되어야 함
- 테스트 DB는 각 테스트마다 새로 생성되고 삭제됨
- 실제 프로덕션 DB를 사용하지 않음
- 리포트 파일은 `.gitignore`에 포함되어 있음 (Git에 커밋되지 않음)
