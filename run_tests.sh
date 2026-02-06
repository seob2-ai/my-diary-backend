#!/bin/bash
# 테스트 실행 스크립트 (Linux/Mac)

echo "========================================"
echo "테스트 실행"
echo "========================================"
echo ""

# 가상환경 활성화
source venv/bin/activate

# pytest 실행
pytest tests/ -v


