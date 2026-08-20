FROM python:3.14-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PYTHON_PREFERENCE=only-system \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim-bookworm
RUN useradd -m -s /bin/bash kiosk
WORKDIR /app

# 💡 순서 변경: 소스 코드를 먼저 복사하고, builder의 .venv를 나중에 덮어씌움
COPY --chown=kiosk:kiosk . .
COPY --chown=kiosk:kiosk --from=builder /app/.venv /app/.venv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

USER kiosk
CMD ["uvicorn", "src.interface.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
