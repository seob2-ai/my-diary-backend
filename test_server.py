"""
서버가 재시작되었는지 확인하는 간단한 테스트 스크립트
"""
import sys

try:
    import requests
    
    # 헬스체크 엔드포인트 테스트
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"✅ 서버가 실행 중입니다!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # 에러 핸들러가 작동하는지 테스트 (의도적으로 잘못된 요청)
        try:
            error_response = requests.post(
                "http://localhost:8000/api/diary",
                json={"invalid": "data"},
                headers={"x-user-id": "test"},
                timeout=2
            )
            print(f"\n✅ 에러 핸들러 테스트:")
            print(f"   Status Code: {error_response.status_code}")
            print(f"   Content-Type: {error_response.headers.get('content-type', 'N/A')}")
            print(f"   Response: {error_response.text[:200]}")
            
            if "application/json" in error_response.headers.get("content-type", ""):
                print(f"\n✅ 성공! 에러가 JSON 형식으로 반환되고 있습니다!")
            else:
                print(f"\n⚠️  경고: 에러가 JSON 형식이 아닙니다.")
                print(f"   서버를 재시작해주세요.")
        except Exception as e:
            print(f"\n⚠️  에러 핸들러 테스트 실패: {e}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버가 실행 중이지 않습니다.")
        print("   다음 명령어로 서버를 시작하세요:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
        
except ImportError:
    print("⚠️  requests 모듈이 설치되어 있지 않습니다.")
    print("   다음 명령어로 설치하세요: pip install requests")
    print("\n또는 브라우저에서 직접 확인:")
    print("   http://localhost:8000/health")
    sys.exit(1)

