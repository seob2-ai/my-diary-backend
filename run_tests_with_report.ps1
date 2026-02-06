# 테스트 실행 및 HTML 리포트 생성 스크립트 (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "테스트 실행 및 리포트 생성" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 저장
$CURRENT_DIR = Get-Location

# 리포트 디렉토리 생성
if (-not (Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}
if (-not (Test-Path "reports\coverage")) {
    New-Item -ItemType Directory -Path "reports\coverage" | Out-Null
}

# 가상환경 활성화
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[WARNING] 가상환경을 찾을 수 없습니다." -ForegroundColor Yellow
}

# pytest 실행 (HTML 리포트 및 커버리지 포함)
Write-Host "테스트 실행 중..." -ForegroundColor Green
pytest tests\ -v

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "리포트 생성 완료!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 절대 경로 생성
$REPORT_PATH = Join-Path $CURRENT_DIR "reports\report.html"
$COVERAGE_PATH = Join-Path $CURRENT_DIR "reports\coverage\index.html"

# 파일 존재 확인
if (Test-Path $REPORT_PATH) {
    Write-Host "[OK] 테스트 리포트 생성됨: $REPORT_PATH" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 테스트 리포트 파일이 없습니다!" -ForegroundColor Red
}

if (Test-Path $COVERAGE_PATH) {
    Write-Host "[OK] 커버리지 리포트 생성됨: $COVERAGE_PATH" -ForegroundColor Green
} else {
    Write-Host "[WARNING] 커버리지 리포트 파일이 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "브라우저에서 열기" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 자동으로 브라우저 열기
if (Test-Path $REPORT_PATH) {
    Write-Host "테스트 리포트를 브라우저에서 엽니다..." -ForegroundColor Green
    Start-Process $REPORT_PATH
    Start-Sleep -Seconds 2
}

if (Test-Path $COVERAGE_PATH) {
    Write-Host "커버리지 리포트를 브라우저에서 엽니다..." -ForegroundColor Green
    Start-Process $COVERAGE_PATH
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "리포트 파일 위치" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "테스트 리포트: $REPORT_PATH"
Write-Host "커버리지 리포트: $COVERAGE_PATH"
Write-Host ""
Write-Host "파일 탐색기에서 열기: explorer reports"
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"


