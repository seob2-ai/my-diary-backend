"""
Phase 1 구현 기능 테스트 스크립트
1. 주간 요약 API
2. 코칭 메시지 통합
3. 일기 분석 미리보기 API
"""
import sys
import json
import os
from datetime import date, timedelta

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

try:
    import requests
    
    BASE_URL = "http://localhost:8016"
    USER_ID = "test-user-phase1"
    
    print("=" * 70)
    print("Phase 1 기능 테스트")
    print("=" * 70)
    
    headers = {
        "x-user-id": USER_ID,
        "Content-Type": "application/json"
    }
    
    # ============================================================
    # 테스트 1: 일기 생성 (코칭 메시지 확인)
    # ============================================================
    print("\n[테스트 1] 일기 생성 및 코칭 메시지 확인")
    print("-" * 70)
    
    test_diary = {
        "content": "오늘은 정말 특별한 하루였다. 새로운 프로젝트를 시작했고, 팀원들과 좋은 아이디어를 나눴다. 내일은 더 나은 하루가 될 것 같다.",
        "emotion": "기쁨과 설렘",
        "event": "새로운 프로젝트 시작",
        "reason": "오랫동안 기다려온 프로젝트였기 때문",
        "insight": "협업의 중요성을 다시 한번 느꼈다",
        "tomorrow": "프로젝트 첫 단계를 완료하고 팀원들과 피드백을 나누겠다"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/diary",
            json=test_diary,
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("[SUCCESS] 일기 생성 성공!")
            print(f"   일기 ID: {data.get('id')}")
            print(f"   모드: {data.get('mode')} - {data.get('mode_label')}")
            print(f"   코칭 메시지: {data.get('coaching', '없음')[:100]}...")
            
            if data.get('coaching'):
                print("   [OK] 코칭 메시지가 정상적으로 생성되었습니다!")
            else:
                print("   [WARNING] 코칭 메시지가 없습니다.")
            
            diary_id = data.get('id')
        else:
            print(f"[FAIL] 일기 생성 실패")
            print(f"   Response: {response.text[:200]}")
            diary_id = None
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        diary_id = None
    
    # ============================================================
    # 테스트 2: 일기 분석 미리보기
    # ============================================================
    print("\n[테스트 2] 일기 분석 미리보기")
    print("-" * 70)
    
    preview_diary = {
        "content": "오늘은 조금 피곤한 하루였다. 하지만 꾸준히 노력하고 있다.",
        "emotion": "피곤함",
        "event": "일상적인 하루",
        "reason": "최근 바쁜 일정 때문"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/diary/preview",
            json=preview_diary,
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] 분석 미리보기 성공!")
            print(f"   모드: {data.get('mode')} - {data.get('mode_label')}")
            print(f"   모드 설명: {data.get('mode_description', '')[:80]}...")
            print(f"   코칭: {data.get('coaching', '')[:80]}...")
            print(f"   모호성: {data.get('is_ambiguous')} (점수: {data.get('ambiguity_score')})")
            if data.get('ambiguity_reasons'):
                print(f"   모호성 이유: {', '.join(data.get('ambiguity_reasons', [])[:2])}")
        else:
            print(f"[FAIL] 분석 미리보기 실패")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
    
    # ============================================================
    # 테스트 3: 주간 요약 API
    # ============================================================
    print("\n[테스트 3] 주간 요약 API")
    print("-" * 70)
    
    try:
        # 이번 주 월요일 날짜 계산
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        response = requests.get(
            f"{BASE_URL}/api/summary/weekly",
            params={"startDate": monday.isoformat()},
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] 주간 요약 조회 성공!")
            print(f"   기간: {data.get('startDate')} ~ {data.get('endDate')}")
            print(f"   총 일기 개수: {data.get('totalEntries')}")
            print(f"   모드별 분포: {json.dumps(data.get('modeCounts', {}), ensure_ascii=False)}")
            highlights = data.get('highlights', {})
            print(f"   하이라이트:")
            print(f"     - 가장 긴 일기 ID: {highlights.get('longestEntryId', '없음')}")
            print(f"     - 가장 짧은 일기 ID: {highlights.get('shortestEntryId', '없음')}")
            print(f"     - 가장 긍정적인 모드: {highlights.get('mostPositiveMode', '없음')}")
        else:
            print(f"[FAIL] 주간 요약 조회 실패")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================
    # 테스트 4: 일기 수정 시 코칭 재생성 확인
    # ============================================================
    if diary_id:
        print("\n[테스트 4] 일기 수정 및 코칭 재생성 확인")
        print("-" * 70)
        
        try:
            update_data = {
                "emotion": "더 나은 감정",
                "insight": "새로운 인사이트를 얻었다"
            }
            
            response = requests.patch(
                f"{BASE_URL}/api/diary/{diary_id}",
                json=update_data,
                headers=headers,
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("[SUCCESS] 일기 수정 성공!")
                print(f"   업데이트된 모드: {data.get('mode')}")
                print(f"   재생성된 코칭: {data.get('coaching', '없음')[:100]}...")
                
                if data.get('coaching'):
                    print("   [OK] 코칭 메시지가 재생성되었습니다!")
            else:
                print(f"[FAIL] 일기 수정 실패")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    
    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("=" * 70)
    
except ImportError:
    print("[WARNING] requests 모듈이 설치되어 있지 않습니다.")
    print("   다음 명령어로 설치하세요: pip install requests")
    print("\n   또는 Swagger UI에서 직접 테스트하세요:")
    print("   http://localhost:8016/docs")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] 예상치 못한 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

