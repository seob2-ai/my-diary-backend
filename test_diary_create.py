"""
일기 생성 API를 테스트하는 스크립트
실제 클라이언트가 보내는 형식으로 요청을 보냅니다.
"""
import sys
import json

try:
    import requests
    
    print("=" * 60)
    print("일기 생성 API 테스트")
    print("=" * 60)
    
    # 테스트 1: content 필드만 있는 경우 (클라이언트 호환성)
    print("\n[테스트 1] content 필드만 있는 요청")
    try:
        response = requests.post(
            "http://localhost:8000/api/diary",
            json={
                "content": "오늘은 정말 좋은 하루였다. 새로운 것을 배웠고, 친구들과 즐거운 시간을 보냈다."
            },
            headers={
                "x-user-id": "test-user-123",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Response Body: {response.text[:500]}")
        
        if response.status_code == 201:
            print("   ✅ 성공! 일기가 생성되었습니다.")
            try:
                data = response.json()
                print(f"   생성된 일기 ID: {data.get('id', 'N/A')}")
            except:
                pass
        elif response.status_code >= 400:
            print(f"   ❌ 에러 발생 (Status: {response.status_code})")
            if "application/json" in response.headers.get("content-type", ""):
                try:
                    error_data = response.json()
                    print(f"   에러 정보: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    print("   ✅ 에러가 JSON 형식으로 반환되고 있습니다!")
                except:
                    print("   ⚠️  JSON 파싱 실패")
            else:
                print("   ⚠️  에러가 JSON 형식이 아닙니다!")
                print("   서버를 재시작해주세요.")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ 서버가 실행 중이지 않습니다.")
        print("   다음 명령어로 서버를 시작하세요:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    # 테스트 2: emotion 필드가 있는 경우
    print("\n[테스트 2] emotion 필드가 있는 요청")
    try:
        response = requests.post(
            "http://localhost:8000/api/diary",
            json={
                "emotion": "기쁨",
                "event": "친구들과 만남",
                "reason": "오랜만에 만나서",
                "tomorrow": "운동하기"
            },
            headers={
                "x-user-id": "test-user-123",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 201:
            print("   ✅ 성공! 일기가 생성되었습니다.")
        elif response.status_code >= 400:
            print(f"   ❌ 에러 발생 (Status: {response.status_code})")
            if "application/json" in response.headers.get("content-type", ""):
                print("   ✅ 에러가 JSON 형식으로 반환되고 있습니다!")
            else:
                print("   ⚠️  에러가 JSON 형식이 아닙니다!")
                
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
    
    # 테스트 3: 잘못된 요청 (에러 핸들러 테스트)
    print("\n[테스트 3] 잘못된 요청 (에러 핸들러 테스트)")
    try:
        response = requests.post(
            "http://localhost:8000/api/diary",
            json={"invalid": "data"},
            headers={
                "x-user-id": "test-user-123",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Response Body: {response.text[:300]}")
        
        if "application/json" in response.headers.get("content-type", ""):
            print("   ✅ 성공! 에러가 JSON 형식으로 반환되고 있습니다!")
        else:
            print("   ⚠️  에러가 JSON 형식이 아닙니다!")
            
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
        
except ImportError:
    print("⚠️  requests 모듈이 설치되어 있지 않습니다.")
    print("   다음 명령어로 설치하세요: pip install requests")
    sys.exit(1)

