@echo off
REM 테스트 실행 및 HTML 리포트 생성 스크립트 (Windows)
echo ========================================
echo 테스트 실행 및 리포트 생성
echo ========================================
echo.

REM 현재 디렉토리 저장
set CURRENT_DIR=%CD%

REM 리포트 디렉토리 생성
if not exist "reports" mkdir reports
if not exist "reports\coverage" mkdir reports\coverage

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM pytest 실행 (HTML 리포트 및 커버리지 포함)
pytest tests\ -v

echo.
echo ========================================
echo 리포트 생성 완료!
echo ========================================
echo.

REM 절대 경로 생성
set REPORT_PATH=%CURRENT_DIR%\reports\report.html
set COVERAGE_PATH=%CURRENT_DIR%\reports\coverage\index.html

REM 파일 존재 확인
if exist "%REPORT_PATH%" (
    echo [OK] 테스트 리포트 생성됨: %REPORT_PATH%
) else (
    echo [ERROR] 테스트 리포트 파일이 없습니다!
)

if exist "%COVERAGE_PATH%" (
    echo [OK] 커버리지 리포트 생성됨: %COVERAGE_PATH%
) else (
    echo [WARNING] 커버리지 리포트 파일이 없습니다.
)

echo.
echo ========================================
echo 브라우저에서 열기
echo ========================================
echo.

REM 자동으로 브라우저 열기
if exist "%REPORT_PATH%" (
    echo 테스트 리포트를 브라우저에서 엽니다...
    start "" "%REPORT_PATH%"
    timeout /t 2 /nobreak >nul
)

if exist "%COVERAGE_PATH%" (
    echo 커버리지 리포트를 브라우저에서 엽니다...
    start "" "%COVERAGE_PATH%"
)

echo.
echo ========================================
echo 리포트 파일 위치
echo ========================================
echo.
echo 테스트 리포트: %REPORT_PATH%
echo 커버리지 리포트: %COVERAGE_PATH%
echo.
echo 파일 탐색기에서 열기: explorer reports
echo.

pause

