#!/bin/bash
# 리포트 파일을 브라우저에서 열기

echo "리포트 파일을 브라우저에서 엽니다..."

if [ -f "reports/report.html" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open reports/report.html
    elif command -v open &> /dev/null; then
        open reports/report.html
    fi
else
    echo "리포트 파일이 없습니다. 먼저 테스트를 실행하세요."
    echo "run_tests_with_report.sh 를 실행하세요."
fi

if [ -f "reports/coverage/index.html" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open reports/coverage/index.html
    elif command -v open &> /dev/null; then
        open reports/coverage/index.html
    fi
fi


