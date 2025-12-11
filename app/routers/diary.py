# app/routers/diary.py

from __future__ import annotations

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

# prefix="/diary" → main.py에서 prefix="/api" 붙으니까
# 최종 경로는 /api/diary, /api/diary/{id}
router = APIRouter(
    prefix="/diary",
    tags=["diary"],
)


def _require_user_id(user_id: Optional[str]) -> str:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="x-user-id 헤더가 필요해요.",
        )
    return user_id


@router.post(
    "",
    response_model=schemas.DiaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_diary(
    diary: schemas.DiaryCreate,
    user_id: Optional[str] = Header(default=None, alias="x-user-id"),
    db: Session = Depends(get_db),
):
    """
    일기 한 건 생성 (AI 분석은 일단 비활성화한 버전)
    """
    user_id = _require_user_id(user_id)

    # 1) Pydantic 모델 → dict
    data = diary.model_dump()

    # 2) date 문자열 → Python date 객체로 변환 (SQLite Date 타입 에러 방지)
    raw_date = data.get("date")
    if raw_date:
        try:
            data["date"] = date_type.fromisoformat(raw_date)
        except ValueError:
            data["date"] = date_type.today()
    else:
        data["date"] = date_type.today()

    # 3) DB 엔티티 생성 (분석 필드는 우선 None)
    db_diary = models.DiaryEntry(
        user_id=user_id,
        mode=None,
        mode_label=None,
        mode_description=None,
        coaching=None,
        **data,
    )

    # 4) DB 저장
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)

    return db_diary


@router.get(
    "",
    response_model=List[schemas.DiaryResponse],
)
def list_diaries(
    user_id: Optional[str] = Header(default=None, alias="x-user-id"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    user_id = _require_user_id(user_id)

    query = (
        db.query(models.DiaryEntry)
        .filter(models.DiaryEntry.user_id == user_id)
        .order_by(
            models.DiaryEntry.date.desc(),
            models.DiaryEntry.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
    )

    return query.all()


@router.get(
    "/{diary_id}",
    response_model=schemas.DiaryResponse,
)
def get_diary(
    diary_id: str,
    user_id: Optional[str] = Header(default=None, alias="x-user-id"),
    db: Session = Depends(get_db),
):
    user_id = _require_user_id(user_id)

    diary = (
        db.query(models.DiaryEntry)
        .filter(
            models.DiaryEntry.id == diary_id,
            models.DiaryEntry.user_id == user_id,
        )
        .first()
    )

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 일기를 찾을 수 없어요.",
        )

    return diary

