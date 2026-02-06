# 리포트 파일을 브라우저에서 열기 (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "리포트 파일 열기" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$CURRENT_DIR = Get-Location
$REPORT_PATH = Join-Path $CURRENT_DIR "reports\report.html"
$COVERAGE_PATH = Join-Path $CURRENT_DIR "reports\coverage\index.html"

if (Test-Path $REPORT_PATH) {
    Write-Host "테스트 리포트를 엽니다..." -ForegroundColor Green
    Start-Process $REPORT_PATH
    Start-Sleep -Seconds 1
} else {
    Write-Host "[ERROR] 리포트 파일이 없습니다: $REPORT_PATH" -ForegroundColor Red
    Write-Host "먼저 .\run_tests_with_report.ps1 를 실행하세요." -ForegroundColor Yellow
    Write-Host ""
}

if (Test-Path $COVERAGE_PATH) {
    Write-Host "커버리지 리포트를 엽니다..." -ForegroundColor Green
    Start-Process $COVERAGE_PATH
} else {
    Write-Host "[WARNING] 커버리지 리포트 파일이 없습니다: $COVERAGE_PATH" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "파일 탐색기에서 reports 폴더 열기..." -ForegroundColor Green
Start-Process explorer.exe -ArgumentList "reports"

Read-Host "계속하려면 Enter를 누르세요"


