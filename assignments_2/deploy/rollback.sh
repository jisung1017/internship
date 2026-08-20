#!/usr/bin/env bash
set -euo pipefail

PREV=${1:?이전 릴리스 SHA를 인자로 입력하세요 (예: ./deploy/rollback.sh b41bbed)}
TARGET="/srv/kiosk/releases/$PREV"

if [ ! -d "$TARGET" ]; then
  echo "에러: 해당 릴리스 디렉터리가 존재하지 않습니다: $TARGET"
  exit 1
fi

# 원자적 심링크 전환 및 서비스 재시작
ln -sfn "$TARGET" /srv/kiosk/current
sudo systemctl restart kiosk

# 헬스체크
sleep 3
systemctl is-active --quiet kiosk && echo "롤백 완료: $PREV"
