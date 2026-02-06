@echo off
REM 리포트를 HTTP 서버로 제공하여 브라우저에서 확인
echo ========================================
echo 리포트 뷰어 서버 시작
echo ========================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM Python 스크립트 실행
python view_reports_server.py

pause


