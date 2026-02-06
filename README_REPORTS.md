# 리포트 확인 가이드

테스트 리포트를 브라우저에서 확인하는 여러 가지 방법입니다.

## 방법 1: 자동으로 브라우저 열기 (추천)

### Windows (CMD)
```bash
run_tests_with_report.bat
```

### Windows (PowerShell) ⭐
```powershell
.\run_tests_with_report.ps1
```

테스트 실행 후 자동으로 브라우저에서 리포트가 열립니다.

## 방법 2: 리포트 파일 직접 열기

### Windows (CMD)
```bash
open_reports.bat
```

### Windows (PowerShell)
```powershell
.\open_reports.ps1
```

또는 수동으로:
1. 파일 탐색기에서 `reports` 폴더 열기
2. `report.html` 파일을 더블클릭하여 브라우저에서 열기
3. `coverage/index.html` 파일도 더블클릭하여 커버리지 확인

## 방법 3: HTTP 서버로 확인 (가장 확실한 방법)

### Windows (CMD)
```bash
view_reports.bat
```

### Windows (PowerShell)
```powershell
.\view_reports.ps1
```

이 방법은:
- 로컬 HTTP 서버를 시작합니다
- 브라우저에서 `http://localhost:8888/report.html`로 접속
- 파일 경로 문제 없이 정상적으로 표시됩니다

### 수동으로 서버 실행
```bash
# 가상환경 활성화
venv\Scripts\activate

# Python 스크립트 실행
python view_reports_server.py
```

브라우저에서 자동으로 열리며, 다음 주소로 접속할 수 있습니다:
- 테스트 리포트: http://localhost:8888/report.html
- 커버리지 리포트: http://localhost:8888/coverage/index.html

## 방법 4: 파일 경로 직접 입력

브라우저 주소창에 다음 경로를 입력:

```
file:///C:/Users/USER/Desktop/my-diary-backend/reports/report.html
```

(실제 경로는 프로젝트 위치에 따라 다를 수 있습니다)

## 문제 해결

### 리포트 파일이 없는 경우
1. 먼저 테스트를 실행하세요:
   ```bash
   run_tests_with_report.bat
   ```

2. `reports` 폴더가 생성되었는지 확인하세요.

3. `reports/report.html` 파일이 있는지 확인하세요.

### 브라우저에서 파일이 열리지 않는 경우
1. **HTTP 서버 사용 (추천)**: `view_reports.bat` 실행
2. **파일 탐색기에서 직접 열기**: `reports` 폴더에서 HTML 파일 더블클릭
3. **브라우저에서 파일 열기**: 브라우저 메뉴 > 파일 > 열기

### 리포트가 제대로 표시되지 않는 경우
- HTTP 서버 방법(`view_reports.bat`)을 사용하면 대부분 해결됩니다.
- 파일 경로에 한글이나 특수문자가 있으면 문제가 될 수 있습니다.

## 리포트 파일 위치

- **테스트 리포트**: `reports/report.html`
- **커버리지 리포트**: `reports/coverage/index.html`

## 빠른 확인

가장 간단한 방법:

### CMD 사용 시:
```bash
# 1. 테스트 실행 및 리포트 생성
run_tests_with_report.bat

# 2. 리포트 확인 (HTTP 서버 사용)
view_reports.bat
```

### PowerShell 사용 시: ⭐
```powershell
# 1. 테스트 실행 및 리포트 생성
.\run_tests_with_report.ps1

# 2. 리포트 확인 (HTTP 서버 사용)
.\view_reports.ps1
```

**참고**: PowerShell에서는 현재 디렉토리의 스크립트를 실행할 때 `.\` 접두사를 붙여야 합니다.

