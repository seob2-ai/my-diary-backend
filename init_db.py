#!/usr/bin/env python
"""
데이터베이스 초기화 스크립트
테이블이 없을 경우 생성합니다.
"""
from app.database import Base, engine
from app import models  # 모델을 import하여 Base에 등록

def init_database():
    """데이터베이스 테이블 생성"""
    print("데이터베이스 테이블 생성 중...")
    try:
        # 모든 모델에서 정의한 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] 데이터베이스 테이블이 성공적으로 생성되었습니다!")
        
        # 생성된 테이블 목록 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"생성된 테이블: {tables}")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        raise

if __name__ == "__main__":
    init_database()

