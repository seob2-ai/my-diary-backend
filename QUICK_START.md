# 빠른 시작 가이드

## PowerShell에서 테스트 실행하기

PowerShell에서는 현재 디렉토리의 스크립트를 실행할 때 `.\` 접두사를 붙여야 합니다.

### 1. 테스트 실행 및 리포트 생성

```powershell
.\run_tests_with_report.ps1
```

또는 CMD 배치 파일 사용:
```powershell
cmd /c run_tests_with_report.bat
```

### 2. 리포트 확인

#### 방법 A: 자동으로 브라우저 열기 (이미 위에서 실행됨)
테스트 실행 후 자동으로 브라우저가 열립니다.

#### 방법 B: HTTP 서버로 확인 (가장 확실)
```powershell
.\view_reports.ps1
```

#### 방법 C: 리포트 파일 직접 열기
```powershell
.\open_reports.ps1
```

## CMD에서 실행하기

CMD 프롬프트를 열고:

```cmd
run_tests_with_report.bat
```

## 문제 해결

### PowerShell 실행 정책 오류
PowerShell에서 스크립트 실행이 차단된 경우:

```powershell
# 현재 세션에서만 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

또는 CMD 배치 파일을 사용하세요:
```powershell
cmd /c run_tests_with_report.bat
```

### 파일을 찾을 수 없다는 오류
현재 디렉토리에서 실행하고 있는지 확인:
```powershell
Get-Location
# 프로젝트 루트 디렉토리인지 확인
```

## 모든 실행 방법 요약

| 방법 | CMD | PowerShell |
|------|-----|-----------|
| 테스트 실행 | `run_tests_with_report.bat` | `.\run_tests_with_report.ps1` |
| 리포트 열기 | `open_reports.bat` | `.\open_reports.ps1` |
| HTTP 서버 | `view_reports.bat` | `.\view_reports.ps1` |


