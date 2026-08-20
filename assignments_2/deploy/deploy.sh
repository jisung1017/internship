#!/usr/bin/env bash
set -euo pipefail

# 1. 현재 커밋의 짧은 SHA 해시 가져오기 (예: b41bbed)
SHA=$(git rev-parse --short HEAD)
DEST=/srv/kiosk/releases/$SHA

# 2. SHA 이름의 새 디렉터리를 만들고 최신 코드 복사
mkdir -p "$DEST"
git archive HEAD | tar -x -C "$DEST"
cd "$DEST"

# 3. 해당 release 전용 독립 가상환경(.venv) 구축 및 의존성 설치
uv sync --frozen

# 4. current 심볼릭 링크를 새 폴더로 즉시 전환 (Atomic Switch)
ln -sfn "$DEST" /srv/kiosk/current

# 5. systemd 서비스 재시작
sudo systemctl restart kiosk

# 6. 정상 동작 헬스체크 (실패 시 배포 오류 처리)
sleep 3
systemctl is-active --quiet kiosk || { sudo journalctl -u kiosk -n 50 --no-pager; exit 1; }
curl -sf http://127.0.0.1:8000/docs -o /dev/null || { echo "헬스체크 실패"; exit 1; }

echo "배포 완료: $SHA"
