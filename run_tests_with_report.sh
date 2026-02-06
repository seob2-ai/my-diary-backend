#!/bin/bash
# 테스트 실행 및 HTML 리포트 생성 스크립트 (Linux/Mac)

echo "========================================"
echo "테스트 실행 및 리포트 생성"
echo "========================================"
echo ""

# 리포트 디렉토리 생성
mkdir -p reports

# 가상환경 활성화
source venv/bin/activate

# pytest 실행 (HTML 리포트 및 커버리지 포함)
pytest tests/ -v

echo ""
echo "========================================"
echo "리포트 생성 완료!"
echo "========================================"
echo ""
echo "다음 파일을 브라우저에서 열어보세요:"
echo "  - reports/report.html (테스트 결과)"
echo "  - reports/coverage/index.html (코드 커버리지)"
echo ""

# Linux/Mac에서 브라우저 열기 (선택사항)
read -p "브라우저에서 자동으로 열까요? (y/n): " open_browser
if [ "$open_browser" = "y" ] || [ "$open_browser" = "Y" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open reports/report.html
        xdg-open reports/coverage/index.html
    elif command -v open &> /dev/null; then
        open reports/report.html
        open reports/coverage/index.html
    fi
fi


