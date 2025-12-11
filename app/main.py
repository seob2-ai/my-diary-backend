# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import diary  # ✅ summary는 당분간 제외


# ---------------------------
# 1. DB 테이블 생성
# ---------------------------
Base.metadata.create_all(bind=engine)


# ---------------------------
# 2. FastAPI 앱 생성
# ---------------------------
app = FastAPI(
    title="My Diary Backend",
    description="갓생·자아성찰 일기 앱용 백엔드 API",
    version="0.1.0",
)


# ---------------------------
# 3. CORS 설정
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# 4. 라우터 등록
# ---------------------------
# ✅ diary 라우터만 사용
app.include_router(diary.router, prefix="/api")


# ---------------------------
# 5. 헬스체크 & 루트
# ---------------------------
@app.get("/", tags=["system"])
def root():
    return {"message": "My Diary Backend is running"}


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

