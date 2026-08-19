#!/bin/bash

# 현재 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

echo ""
echo "===================================="
echo "       Weather Outfit AI (Mac)"
echo "===================================="
echo ""

# 1. 가상환경 확인 및 생성
if [ ! -d ".venv" ]; then
    echo "[1/3] 가상환경(.venv)을 생성하는 중입니다..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Python3 설치 여부를 확인해주세요."
        read -p "엔터 키를 누르면 종료됩니다..."
        exit 1
    fi
fi

# 2. 필요한 모듈 설치
echo "[2/3] 필요한 라이브러리를 확인 및 설치하고 있습니다..."
./.venv/bin/pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ 라이브러리 설치에 실패했습니다."
    read -p "엔터 키를 누르면 종료됩니다..."
    exit 1
fi

# 3. 브라우저 자동으로 열기 (백그라운드 실행)
echo "[3/3] Weather Outfit AI를 실행합니다..."
(sleep 2 && open http://127.0.0.1:5000) &

# 4. Flask 서버 실행
./.venv/bin/python app.py