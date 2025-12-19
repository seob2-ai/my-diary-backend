@echo off
chcp 65001 >nul
echo 서버를 시작합니다...
echo 클라이언트에서 요청을 보내면 이 창에 로그가 출력됩니다.
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.

REM 가상 환경 활성화
call venv\Scripts\activate.bat

REM 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8016

pause

