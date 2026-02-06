# 리포트를 HTTP 서버로 제공하여 브라우저에서 확인 (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "리포트 뷰어 서버 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 가상환경 활성화
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Python 스크립트 실행
python view_reports_server.py


