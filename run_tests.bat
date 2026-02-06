@echo off
REM 테스트 실행 스크립트 (Windows)
echo ========================================
echo 테스트 실행
echo ========================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM pytest 실행
pytest tests\ -v

pause


