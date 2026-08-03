import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 프로젝트 루트 경로를 sys.path에 추가하여 src 모듈을 임포트할 수 있도록 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.models import Base

# Alembic Config 객체
config = context.config

# 로깅 설정 적용
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ORM 모델 메타데이터 등록 (Auto-Migration 핵심)
target_metadata = Base.metadata


def get_url() -> str:
    """환경 변수 DATABASE_URL을 읽어오며, psycopg3 호환 스킴(postgresql+psycopg://)을 보장합니다."""
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return db_url


def run_migrations_offline() -> None:
    """'오프라인' 모드 마이그레이션 실행 (SQL 스크립트 추출용)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지 옵션
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'온라인' 모드 마이그레이션 실행 (실제 DB 연결 후 적용)."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경 감지 옵션
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()