# 디버깅 가이드

## 현재 문제
- 500 Internal Server Error 발생
- 응답 본문이 비어있음
- `content-type: text/plain`으로 반환됨

## 확인 사항

### 1. 서버 콘솔 로그 확인 (가장 중요!)

서버를 실행한 터미널/콘솔에서 다음을 확인하세요:

#### 정상적인 경우:
```
INFO:     요청 시작: POST http://localhost:8000/api/diary
INFO:     일기 생성 요청 시작: user_id=...
INFO:     Payload: ...
```

#### 에러가 발생한 경우:
```
ERROR:    예상치 못한 오류: ...
ERROR:    Traceback (most recent call last):
  ...
```

**서버 콘솔에 출력된 에러 메시지를 복사해서 공유해주세요!**

### 2. 서버 재시작 확인

1. 서버 완전히 중지 (Ctrl+C)
2. 다시 시작:
   ```bash
   uvicorn app.main:app --reload
   ```

### 3. 테스트 요청

브라우저에서:
- http://localhost:8000/health 접속 → `{"status":"ok"}` 확인
- http://localhost:8000/docs 접속 → Swagger UI 확인

## 다음 단계

서버 콘솔에 출력된 **전체 에러 메시지와 Traceback**을 공유해주시면 정확한 원인을 파악할 수 있습니다.

