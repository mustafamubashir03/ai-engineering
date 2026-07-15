FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --group dev --no-install-project

COPY . .
RUN uv sync --group dev

EXPOSE 8888

CMD ["sleep", "infinity"]
