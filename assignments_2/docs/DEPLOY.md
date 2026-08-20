# Kiosk API 배포 및 운영 가이드

이 문서는 신규 VM 세팅부터 배포, 롤백, 장애 대응까지의 모든 과정을 담고 있습니다.
모든 명령어는 복사하여 즉시 실행할 수 있습니다.

## 1. 서버 초기 세팅 (New VM)

### 1-1. 필수 패키지 설치
```bash
sudo apt update && sudo apt install -y git docker.io ufw tailscale
1-2. 배포용 계정 및 디렉터리 생성
Bash
sudo useradd -r -s /bin/false kiosk
sudo mkdir -p /srv/kiosk/releases
sudo chown -R $USER:$USER /srv/kiosk
1-3. 환경변수 설정
Bash
sudo mkdir -p /etc/kiosk
sudo bash -c 'cat <<EOT> /etc/kiosk/kiosk.env
DATABASE_URL=postgresql://kiosk:jisung@127.0.0.1:5432/kiosk
EOT'
sudo chown kiosk:kiosk /etc/kiosk/kiosk.env
sudo chmod 600 /etc/kiosk/kiosk.env
2. 배포 및 롤백 절차
배포 (Deploy)
Bash
./deploy/deploy.sh
롤백 (Rollback)
Bash
# 1. 릴리스 목록(SHA) 확인
ls -l /srv/kiosk/releases
# 2. 롤백 실행
./deploy/rollback.sh <이전_SHA>
3. 마이그레이션이 포함된 롤백
주의: 컬럼을 지우는 마이그레이션 롤백
DROP COLUMN 실행 시 물리적 데이터가 소실되므로 코드만 롤백하면 에러가 발생합니다. 가급적 코드 레벨에서 사용을 중단하고 나중에 컬럼을 지우는 방식을 사용하세요. 모든 마이그레이션은 downgrade()가 작성되어 있어야 합니다.

데이터베이스 롤백이 필요한 경우 절차

Bash
# 1. DB 다운그레이드 (심링크 롤백 전 수행)
/srv/kiosk/current/.venv/bin/alembic downgrade -1

# 2. 애플리케이션 롤백
./deploy/rollback.sh <이전_SHA>
4. 장애 시 점검 순서
서비스 기동 상태 확인

Bash
systemctl status kiosk
실시간 로그 및 에러 원인 확인

Bash
sudo journalctl -u kiosk -n 50 --no-pager
DB 컨테이너 확인 및 연결 테스트

Bash
docker ps | grep kiosk-db
docker exec kiosk-db pg_isready -U kiosk
