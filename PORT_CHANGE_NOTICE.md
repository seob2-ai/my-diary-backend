# 포트 변경 안내

## 변경 사항

백엔드 서버 포트가 **8000 → 8016**으로 변경되었습니다.

## 프론트엔드 프록시 설정 변경 필요

프론트엔드 프로젝트의 `vite.config.js` 또는 `vite.config.ts` 파일에서 프록시 설정을 다음과 같이 변경해주세요:

### 변경 전:
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // ❌ 이전 포트
        changeOrigin: true,
      }
    }
  }
}
```

### 변경 후:
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8016',  // ✅ 새로운 포트
        changeOrigin: true,
      }
    }
  }
}
```

## 서버 실행

이제 다음 명령어로 서버를 실행하면 8016 포트에서 실행됩니다:

```bash
start_server.bat
```

또는 직접 실행:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8016
```

## 확인 방법

서버가 정상적으로 실행되었는지 확인:

1. 브라우저에서 접속: `http://localhost:8016/health`
   - `{"status":"ok"}` 응답이 오면 정상

2. Swagger UI 접속: `http://localhost:8016/docs`
   - API 문서가 보이면 정상

## 중요 사항

⚠️ **프론트엔드 프록시 설정을 변경한 후에는 Vite 개발 서버를 재시작해야 합니다!**

1. 프론트엔드 `vite.config.js` 파일 수정
2. Vite 개발 서버 재시작 (Ctrl+C 후 다시 시작)
3. 클라이언트에서 일기 저장 테스트

