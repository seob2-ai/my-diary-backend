import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app import models, schemas
from app.services.analysis_service import analyze_mode, generate_coaching, detect_ambiguity
from app.dependencies import get_current_user_id
from app.utils import (
    DictLike,
    parse_date_or_today,
    normalize_analysis_result,
    create_diary_like_from_payload,
    create_diary_like_from_entry,
    generate_coaching_safely,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["diary"])


@router.get("/diary/test")
def diary_test():
    return {"message": "diary router works"}


@router.get(
    "/diary",
    response_model=List[schemas.DiaryResponse],
)
def list_diaries(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    date_: Optional[str] = Query(default=None, alias="date", description="YYYY-MM-DD"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """유저별 일기 목록 조회"""
    q = db.query(models.DiaryEntry).filter(models.DiaryEntry.user_id == user_id)

    if date_:
        q = q.filter(models.DiaryEntry.date == parse_date_or_today(date_))

    rows = (
        q.order_by(models.DiaryEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return rows


@router.post(
    "/diary",
    response_model=schemas.DiaryResponse,
    status_code=201,
)
def create_diary(
    payload: schemas.DiaryCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """일기 저장"""
    try:
        logger.info(f"일기 생성 요청 시작: user_id={user_id}")
        logger.debug(f"Payload: {payload}")
        
        # 날짜 처리
        try:
            diary_date = parse_date_or_today(payload.date)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"날짜 파싱 오류: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"날짜 처리 중 오류가 발생했습니다: {str(e)}"
            )
        
        # DictLike 객체 생성
        diary_like = create_diary_like_from_payload(payload)

        try:
            raw = analyze_mode(diary_like)
            analysis = normalize_analysis_result(raw)
        except Exception as e:
            logger.error(f"분석 모드 오류: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"일기 분석 중 오류가 발생했습니다: {str(e)}"
            )

        logger.info(f"분석 결과: mode={analysis.get('mode')}")

        # 코칭 메시지 생성
        coaching_message = generate_coaching_safely(diary_like, analysis, logger)

        try:
            emotion = diary_like.emotion
            db_diary = models.DiaryEntry(
                id=models.make_diary_id(),
                user_id=user_id,
                date=diary_date,
                emotion=emotion,
                event=payload.event or "",
                reason=payload.reason or "",
                insight=payload.insight or "",
                tomorrow=payload.tomorrow or "",
                mode=analysis.get("mode"),
                mode_label=analysis.get("mode_label"),
                mode_description=analysis.get("mode_description"),
                coaching=coaching_message,  # 생성된 코칭 메시지 저장
                analysis_meta=analysis.get("analysis_meta"),
            )

            db.add(db_diary)
            db.commit()
            db.refresh(db_diary)
            logger.info(f"일기 생성 성공: id={db_diary.id}")
            
            return db_diary
        except Exception as e:
            # 트랜잭션 롤백
            db.rollback()
            logger.error(f"DB 저장 오류: {type(e).__name__}: {str(e)}", exc_info=True)
            # 예외를 다시 발생시켜 전역 예외 핸들러가 처리하도록 함
            raise
    except HTTPException:
        # HTTPException은 그대로 전달
        raise
    except Exception as e:
        # 예상치 못한 모든 예외를 잡아서 로깅하고 HTTPException으로 변환
        logger.error(f"예상치 못한 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/diary/{diary_id}",
    response_model=schemas.DiaryResponse,
)
def get_diary(
    diary_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """일기 단건 조회"""
    row = (
        db.query(models.DiaryEntry)
        .filter(models.DiaryEntry.id == diary_id)
        .filter(models.DiaryEntry.user_id == user_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없습니다.")
    return row


@router.patch(
    "/diary/{diary_id}",
    response_model=schemas.DiaryResponse,
)
def update_diary(
    diary_id: str,
    payload: schemas.DiaryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    일기 수정 (부분 업데이트 지원)
    - 제공된 필드만 업데이트
    - 수정 시 분석 모드도 재계산됨
    """
    try:
        # 일기 조회
        diary = (
            db.query(models.DiaryEntry)
            .filter(models.DiaryEntry.id == diary_id)
            .filter(models.DiaryEntry.user_id == user_id)
            .first()
        )
        
        if not diary:
            raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없습니다.")
        
        logger.info(f"일기 수정 요청: diary_id={diary_id}, user_id={user_id}")
        
        # 업데이트할 필드만 변경
        update_data = payload.model_dump(exclude_unset=True)
        
        # 날짜 처리
        if "date" in update_data and update_data["date"]:
            try:
                diary.date = parse_date_or_today(update_data["date"])
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"날짜 파싱 오류: {type(e).__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=400,
                    detail=f"날짜 처리 중 오류가 발생했습니다: {str(e)}"
                )
        
        # content 필드 처리 (emotion으로 매핑)
        if "content" in update_data and update_data["content"]:
            if "emotion" not in update_data or not update_data["emotion"]:
                update_data["emotion"] = update_data["content"]
        
        # 필드 업데이트
        for field, value in update_data.items():
            if field not in ["date", "content"] and value is not None:
                setattr(diary, field, value)
        
        # emotion 필드 업데이트 (content에서 매핑된 경우 포함)
        if "emotion" in update_data:
            diary.emotion = update_data["emotion"] or diary.emotion
        
        # 분석 모드 재계산 (내용이 변경된 경우)
        if any(field in update_data for field in ["emotion", "event", "reason", "insight", "tomorrow"]):
            diary_like = create_diary_like_from_entry(diary)
            
            try:
                raw = analyze_mode(diary_like)
                analysis = normalize_analysis_result(raw)
                
                # 분석 결과 업데이트
                diary.mode = analysis.get("mode")
                diary.mode_label = analysis.get("mode_label")
                diary.mode_description = analysis.get("mode_description")
                diary.analysis_meta = analysis.get("analysis_meta")
                
                # 코칭 메시지 재생성
                coaching_message = generate_coaching_safely(diary_like, analysis, logger)
                if coaching_message:
                    diary.coaching = coaching_message
                
                logger.info(f"분석 모드 재계산 완료: mode={diary.mode}")
            except Exception as e:
                logger.error(f"분석 모드 재계산 오류: {type(e).__name__}: {str(e)}", exc_info=True)
                # 분석 실패해도 일기 수정은 진행
        
        # 업데이트 시간 갱신
        diary.updated_at = datetime.now()
        
        db.commit()
        db.refresh(diary)
        logger.info(f"일기 수정 성공: id={diary.id}")
        
        return diary
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"일기 수정 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"일기 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete(
    "/diary/{diary_id}",
    status_code=204,
)
def delete_diary(
    diary_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """일기 삭제"""
    try:
        diary = (
            db.query(models.DiaryEntry)
            .filter(models.DiaryEntry.id == diary_id)
            .filter(models.DiaryEntry.user_id == user_id)
            .first()
        )
        
        if not diary:
            raise HTTPException(status_code=404, detail="해당 일기를 찾을 수 없습니다.")
        
        logger.info(f"일기 삭제 요청: diary_id={diary_id}, user_id={user_id}")
        
        db.delete(diary)
        db.commit()
        
        logger.info(f"일기 삭제 성공: id={diary_id}")
        return Response(status_code=204)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"일기 삭제 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"일기 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/diary/stats",
    response_model=schemas.DiaryStatsResponse,
)
def get_diary_stats(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    일기 통계 정보 조회
    - 전체 일기 개수
    - 이번 달/주 일기 개수
    - 모드별 분포
    - 가장 오래된/최근 일기 날짜
    """
    try:
        logger.info(f"일기 통계 조회 요청: user_id={user_id}")
        
        # 기본 쿼리
        base_query = db.query(models.DiaryEntry).filter(
            models.DiaryEntry.user_id == user_id
        )
        
        # 전체 개수
        total_count = base_query.count()
        
        # 날짜 범위 계산
        today = datetime.now().date()
        this_month_start = date(today.year, today.month, 1)
        this_week_start = today - timedelta(days=today.weekday())
        
        # 이번 달 개수
        this_month_count = base_query.filter(
            models.DiaryEntry.date >= this_month_start
        ).count()
        
        # 이번 주 개수
        this_week_count = base_query.filter(
            models.DiaryEntry.date >= this_week_start
        ).count()
        
        # 모드별 분포
        mode_counts = (
            db.query(models.DiaryEntry.mode, func.count(models.DiaryEntry.id))
            .filter(models.DiaryEntry.user_id == user_id)
            .filter(models.DiaryEntry.mode.isnot(None))
            .group_by(models.DiaryEntry.mode)
            .all()
        )
        mode_distribution = {mode: count for mode, count in mode_counts if mode}
        
        # 가장 오래된/최근 일기 날짜
        date_range = (
            db.query(
                func.min(models.DiaryEntry.date).label("earliest"),
                func.max(models.DiaryEntry.date).label("latest")
            )
            .filter(models.DiaryEntry.user_id == user_id)
            .first()
        )
        
        earliest_date = date_range.earliest if date_range else None
        latest_date = date_range.latest if date_range else None
        
        stats = schemas.DiaryStatsResponse(
            total_count=total_count,
            this_month_count=this_month_count,
            this_week_count=this_week_count,
            mode_distribution=mode_distribution,
            earliest_date=earliest_date,
            latest_date=latest_date,
        )
        
        logger.info(f"통계 조회 성공: total={total_count}, this_month={this_month_count}")
        
        return stats
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/diary/search",
    response_model=List[schemas.DiaryResponse],
)
def search_diaries(
    q: str = Query(..., description="검색어 (emotion, event, reason, insight, tomorrow, coaching 필드에서 검색)"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    일기 검색
    - emotion, event, reason, insight, tomorrow, coaching 필드에서 검색어 포함 여부 확인
    - 대소문자 구분 없음
    """
    try:
        logger.info(f"일기 검색 요청: user_id={user_id}, query={q}")
        
        if not q or not q.strip():
            raise HTTPException(
                status_code=400,
                detail="검색어를 입력해주세요."
            )
        
        search_term = f"%{q.strip()}%"
        
        # 여러 필드에서 검색 (OR 조건)
        # emotion, event, reason, insight, tomorrow, coaching 필드에서 검색
        # NULL 값 처리를 위해 coaching 필드는 NULL 체크 추가
        search_conditions = [
            models.DiaryEntry.emotion.ilike(search_term),
            models.DiaryEntry.event.ilike(search_term),
            models.DiaryEntry.reason.ilike(search_term),
            models.DiaryEntry.insight.ilike(search_term),
            models.DiaryEntry.tomorrow.ilike(search_term),
        ]
        
        # coaching 필드는 NULL이 아닐 때만 검색
        search_conditions.append(
            (models.DiaryEntry.coaching.isnot(None)) & 
            (models.DiaryEntry.coaching.ilike(search_term))
        )
        
        results = (
            db.query(models.DiaryEntry)
            .filter(models.DiaryEntry.user_id == user_id)
            .filter(or_(*search_conditions))
            .order_by(models.DiaryEntry.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"검색 결과: {len(results)}개 일기 발견")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"검색 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/diary/preview",
    response_model=schemas.DiaryAnalysisResult,
)
def preview_diary_analysis(
    payload: schemas.DiaryCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    일기 분석 결과 미리보기 (저장 없이)
    - 저장 전에 분석 결과를 확인할 수 있음
    - 모드, 모호성, 코칭 메시지 등을 미리 확인 가능
    """
    try:
        logger.info(f"일기 분석 미리보기 요청: user_id={user_id}")
        
        # DictLike 객체 생성
        diary_like = create_diary_like_from_payload(payload)
        
        # 모호성 판단
        try:
            amb_result = detect_ambiguity(diary_like)
        except Exception as e:
            logger.error(f"모호성 판단 오류: {type(e).__name__}: {str(e)}", exc_info=True)
            amb_result = None
        
        # 모드 분석
        try:
            raw = analyze_mode(diary_like)
            analysis = normalize_analysis_result(raw)
        except Exception as e:
            logger.error(f"분석 모드 오류: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"일기 분석 중 오류가 발생했습니다: {str(e)}"
            )
        
        # 코칭 메시지 생성
        coaching_message = generate_coaching_safely(diary_like, analysis, logger)
        
        # 모호성 정보 추출 (analysis_meta에서 또는 직접 계산)
        if amb_result:
            is_ambiguous = amb_result.is_ambiguous
            ambiguity_score = amb_result.score
            ambiguity_reasons = amb_result.reasons
        else:
            # analysis_meta에서 추출 시도
            amb_info = analysis.get("analysis_meta", {}).get("ambiguity", {})
            is_ambiguous = amb_info.get("is_ambiguous", False)
            ambiguity_score = amb_info.get("score", 0.0)
            ambiguity_reasons = amb_info.get("reasons", [])
        
        # DiaryAnalysisResult 생성
        result = schemas.DiaryAnalysisResult(
            mode=analysis.get("mode"),
            mode_label=analysis.get("mode_label"),
            mode_description=analysis.get("mode_description"),
            coaching=coaching_message,
            is_ambiguous=is_ambiguous,
            ambiguity_score=ambiguity_score,
            ambiguity_reasons=ambiguity_reasons,
            analysis_meta=analysis.get("analysis_meta"),
        )
        
        logger.info(f"분석 미리보기 완료: mode={result.mode}, is_ambiguous={result.is_ambiguous}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 미리보기 오류: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"분석 미리보기 중 오류가 발생했습니다: {str(e)}"
        )

