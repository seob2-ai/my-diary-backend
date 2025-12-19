# app/main.py

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import traceback
import logging

from app.database import Base, engine
from app.routers import diary, summary

# 로깅 설정 (더 상세한 로깅)
import os
from logging.handlers import RotatingFileHandler

# 로그 디렉토리 생성
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 파일 핸들러 추가 (로그 파일로 저장)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "server.log"),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# 콘솔 핸들러 추가 (터미널에 출력)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# 루트 로거 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


# ---------------------------
# 1. DB 테이블 생성
# ---------------------------
Base.metadata.create_all(bind=engine)


# ---------------------------
# 2. 커스텀 에러 핸들러 (JSON 응답 보장)
# ---------------------------
async def json_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    ServerErrorMiddleware에서 사용할 JSON 에러 핸들러
    모든 예외를 JSON 형식으로 반환
    """
    error_traceback = traceback.format_exc()
    logger.error(f"ServerErrorMiddleware에서 서버 에러 발생: {type(exc).__name__}: {str(exc)}\n{error_traceback}")
    
    try:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": type(exc).__name__,
                "message": str(exc),
            },
            headers={"Content-Type": "application/json"},
        )
    except Exception as inner_e:
        # JSONResponse 생성 실패 시 최소한의 응답 반환
        logger.critical(f"ServerErrorMiddleware에서 JSONResponse 생성 실패: {type(inner_e).__name__}: {str(inner_e)}", exc_info=True)
        from starlette.responses import Response
        return Response(
            content=f'{{"error":"{type(exc).__name__}","message":"{str(exc)}"}}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )


# ---------------------------
# 3. FastAPI 앱 생성 (exception_handlers 전달)
# ---------------------------
# Starlette가 자동으로 추가하는 ServerErrorMiddleware가 이 핸들러를 사용하도록 설정
app = FastAPI(
    title="My Diary Backend",
    description="갓생·자아성찰 일기 앱용 백엔드 API",
    version="0.1.0",
    exception_handlers={
        500: json_server_error_handler,
        Exception: json_server_error_handler,
    },
)


# ---------------------------
# 5. 전역 예외 핸들러 설정
# ---------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    모든 예외를 잡아서 JSON 형식으로 반환
    """
    import traceback
    error_traceback = traceback.format_exc()
    logger.error(f"전역 예외 핸들러에서 예외 발생: {type(exc).__name__}: {str(exc)}\n{error_traceback}")
    
    # 개발 환경에서는 상세한 에러 정보 포함
    error_detail = {
        "error": type(exc).__name__,
        "message": str(exc),
    }
    
    # 프로덕션 환경에서는 상세 정보 숨김
    # import os
    # if os.getenv("ENVIRONMENT") != "development":
    #     error_detail = {"error": "Internal Server Error", "message": "서버에서 오류가 발생했습니다."}
    
    try:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail,
        )
    except Exception as inner_e:
        # JSONResponse 생성 실패 시 최소한의 응답 반환
        logger.critical(f"전역 예외 핸들러에서 JSONResponse 생성 실패: {type(inner_e).__name__}: {str(inner_e)}", exc_info=True)
        from starlette.responses import Response
        return Response(
            content=f'{{"error":"{type(exc).__name__}","message":"{str(exc)}"}}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTPException을 JSON 형식으로 반환
    """
    logger.error(f"HTTPException 발생: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": str(exc.detail) if exc.detail else "An error occurred",
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    요청 검증 에러를 JSON 형식으로 반환
    """
    logger.error(f"ValidationError 발생: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "요청 데이터가 올바르지 않습니다.",
            "details": exc.errors(),
        },
    )


# ---------------------------
# 4. 요청/응답 미들웨어 (디버깅용) - 가장 먼저 추가
# ---------------------------
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        logger.info(f"요청 시작: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"응답 완료: {response.status_code}")
            return response
        except (HTTPException, StarletteHTTPException) as e:
            # HTTPException은 JSON으로 변환하여 반환
            logger.error(f"미들웨어에서 HTTPException 발생: {e.status_code} - {e.detail}")
            try:
                return JSONResponse(
                    status_code=e.status_code,
                    content={
                        "error": "HTTPException",
                        "message": str(e.detail) if e.detail else "An error occurred",
                        "status_code": e.status_code,
                    },
                )
            except Exception as inner_e:
                # JSONResponse 생성 실패 시 최소한의 응답 반환
                logger.critical(f"JSONResponse 생성 실패: {type(inner_e).__name__}: {str(inner_e)}", exc_info=True)
                from starlette.responses import Response
                return Response(
                    content=f'{{"error":"HTTPException","message":"{str(e.detail)}","status_code":{e.status_code}}}',
                    status_code=e.status_code,
                    media_type="application/json",
                )
        except Exception as e:
            # 모든 예외를 JSON으로 변환하여 반환
            error_traceback = traceback.format_exc()
            logger.error(f"미들웨어에서 예외 발생: {type(e).__name__}: {str(e)}\n{error_traceback}")
            try:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": type(e).__name__,
                        "message": str(e),
                    },
                )
            except Exception as inner_e:
                # JSONResponse 생성 실패 시 최소한의 응답 반환
                logger.critical(f"JSONResponse 생성 실패: {type(inner_e).__name__}: {str(inner_e)}", exc_info=True)
                from starlette.responses import Response
                return Response(
                    content=f'{{"error":"{type(e).__name__}","message":"{str(e)}"}}',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    media_type="application/json",
                )

app.add_middleware(LoggingMiddleware)


# ---------------------------
# 6. CORS 설정
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# 7. 라우터 등록
# ---------------------------
app.include_router(diary.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


# ---------------------------
# 8. 헬스체크 & 루트
# ---------------------------
@app.get("/", tags=["system"])
def root():
    return {"message": "My Diary Backend is running"}


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

