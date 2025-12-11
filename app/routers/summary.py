# app/routers/summary.py
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional, Dict

from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["summary"])


def get_user_id(x_user_id: Optional[str] = Header(default=None)):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "MISSING_USER_ID", "message": "X-User-Id 헤더가 필요합니다."},
        )
    return x_user_id


@router.get(
    "/summary/weekly",
    response_model=schemas.WeeklySummaryResponse,
)
def get_weekly_summary(
    startDate: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    if not startDate:
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        startDate = monday

    endDate = startDate + timedelta(days=6)

    entries = (
        db.query(models.DiaryEntry)
        .filter(
            models.DiaryEntry.user_id == user_id,
            models.DiaryEntry.date >= startDate,
            models.DiaryEntry.date <= endDate,
        )
        .all()
    )

    mode_counts: Dict[str, int] = {}
    longest_id = None
    shortest_id = None
    longest_len = -1
    shortest_len = 10**9

    for e in entries:
        if e.mode:
            mode_counts[e.mode] = mode_counts.get(e.mode, 0) + 1

        combined = " ".join(
            [e.emotion or "", e.event or "", e.reason or "", e.insight or "", e.tomorrow or ""]
        ).strip()
        l = len(combined)
        if l > longest_len:
            longest_len = l
            longest_id = e.id
        if l < shortest_len:
            shortest_len = l
            shortest_id = e.id

    most_positive_mode = None
    if mode_counts:
        # 임시 규칙: growth > stable > routine > slump
        priority = {"growth": 4, "stable": 3, "routine": 2, "slump": 1}
        most_positive_mode = sorted(
            mode_counts.items(),
            key=lambda kv: priority.get(kv[0], 0),
            reverse=True,
        )[0][0]

    return schemas.WeeklySummaryResponse(
        startDate=startDate,
        endDate=endDate,
        totalEntries=len(entries),
        modeCounts=mode_counts,
        highlights={
            "longestEntryId": longest_id,
            "shortestEntryId": shortest_id,
            "mostPositiveMode": most_positive_mode,
        },
    )
