# Gate A0 container skeleton. Docker validation is recorded separately because
# Docker Desktop is not installed on the current workstation.
FROM node:22.17.1-bookworm-slim AS web-build
WORKDIR /workspace/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12.14-slim-bookworm
WORKDIR /workspace
RUN pip install --no-cache-dir uv==0.12.10
COPY apps/api/pyproject.toml apps/api/uv.lock ./apps/api/
RUN uv sync --project ./apps/api --locked --no-dev --no-install-project
COPY apps/api/ ./apps/api/
COPY data/ ./data/
COPY --from=web-build /workspace/apps/web/dist ./apps/web/dist
RUN uv sync --project ./apps/api --locked --no-dev
EXPOSE 8000
CMD ["uv", "run", "--project", "apps/api", "uvicorn", "resilitrip.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
