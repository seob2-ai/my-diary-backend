@echo off
REM 리포트 파일을 브라우저에서 열기
echo ========================================
echo 리포트 파일 열기
echo ========================================
echo.

set CURRENT_DIR=%CD%
set REPORT_PATH=%CURRENT_DIR%\reports\report.html
set COVERAGE_PATH=%CURRENT_DIR%\reports\coverage\index.html

if exist "%REPORT_PATH%" (
    echo 테스트 리포트를 엽니다...
    start "" "%REPORT_PATH%"
    timeout /t 1 /nobreak >nul
) else (
    echo [ERROR] 리포트 파일이 없습니다: %REPORT_PATH%
    echo 먼저 run_tests_with_report.bat 를 실행하세요.
    echo.
)

if exist "%COVERAGE_PATH%" (
    echo 커버리지 리포트를 엽니다...
    start "" "%COVERAGE_PATH%"
) else (
    echo [WARNING] 커버리지 리포트 파일이 없습니다: %COVERAGE_PATH%
    echo.
)

echo 파일 탐색기에서 reports 폴더 열기...
explorer reports

pause
