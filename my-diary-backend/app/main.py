# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import diary


# ---------------------------
# 1. DB 테이블 생성 (초기 1번)
# ---------------------------
# models.py에서 Base = declarative_base() 로 정의했다는 전제
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
# 3. CORS 설정 (프론트에서 호출할 때를 대비)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 개발 단계라 일단 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# 4. 라우터 등록
# ---------------------------
# 👉 여기에서만 prefix="/api"를 붙인다.
#    diary.py 안의 경로는 "/diary", "/diary/{id}" 형태여야 한다.
app.include_router(diary.router, prefix="/api")


# ---------------------------
# 5. 헬스체크 / 루트 엔드포인트
# ---------------------------
@app.get("/", tags=["system"])
def root():
    return {"message": "My Diary Backend is running"}


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
