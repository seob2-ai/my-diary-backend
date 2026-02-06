"""
간단한 HTTP 서버로 리포트 파일을 브라우저에서 확인
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8888
REPORTS_DIR = Path("reports")

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """커스텀 HTTP 요청 핸들러"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPORTS_DIR.absolute()), **kwargs)
    
    def end_headers(self):
        # CORS 헤더 추가 (필요한 경우)
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    """메인 함수"""
    # reports 디렉토리 확인
    if not REPORTS_DIR.exists():
        print(f"[ERROR] reports 디렉토리가 없습니다!")
        print(f"먼저 run_tests_with_report.bat 를 실행하여 리포트를 생성하세요.")
        return
    
    # 리포트 파일 확인
    report_file = REPORTS_DIR / "report.html"
    coverage_file = REPORTS_DIR / "coverage" / "index.html"
    
    if not report_file.exists():
        print(f"[WARNING] 리포트 파일이 없습니다: {report_file}")
    
    # 서버 시작
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 60)
            print("리포트 뷰어 서버 시작")
            print("=" * 60)
            print(f"\n서버 주소: http://localhost:{PORT}")
            print(f"\n리포트 파일:")
            if report_file.exists():
                print(f"  - 테스트 리포트: http://localhost:{PORT}/report.html")
            if coverage_file.exists():
                print(f"  - 커버리지 리포트: http://localhost:{PORT}/coverage/index.html")
            print(f"\n서버를 중지하려면 Ctrl+C를 누르세요.")
            print("=" * 60)
            print()
            
            # 브라우저 자동 열기
            if report_file.exists():
                webbrowser.open(f"http://localhost:{PORT}/report.html")
            if coverage_file.exists():
                import time
                time.sleep(1)
                webbrowser.open(f"http://localhost:{PORT}/coverage/index.html")
            
            # 서버 실행
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98 or "Address already in use" in str(e):
            print(f"[ERROR] 포트 {PORT}가 이미 사용 중입니다.")
            print(f"다른 프로그램이 사용 중이거나 이미 서버가 실행 중일 수 있습니다.")
        else:
            print(f"[ERROR] 서버 시작 실패: {e}")
    except KeyboardInterrupt:
        print("\n\n서버를 종료합니다...")
    except Exception as e:
        print(f"[ERROR] 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()


