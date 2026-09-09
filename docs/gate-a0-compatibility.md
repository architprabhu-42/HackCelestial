# Gate A0 compatibility record

Status: historical record — passed when captured; not a current verification result.

## Runtime and tooling

| Item | Exact version |
|---|---|
| Python | CPython 3.12.14, uv-managed in `.tools/python` |
| Node | 22.17.1 |
| npm | 10.9.2 |
| uv | 0.12.10 |
| SQLite | Python-bundled SQLite (verified through required PRAGMAs) |
| Playwright | 1.54.1 |
| Chromium | 139.0.7258.5, Playwright build 1181 |

## Locked direct dependencies

Python runtime: FastAPI 0.115.12, Pydantic 2.11.7, SQLAlchemy 2.0.41,
Alembic 1.16.4, NetworkX 3.5, Uvicorn 0.35.0.

Python development: pytest 8.4.1, Hypothesis 6.137.0, HTTPX 0.28.1.

Frontend runtime: React 19.1.0, React DOM 19.1.0, MapLibre GL 5.6.0 and
`@xyflow/react` 12.8.2.

Frontend development: TypeScript 5.8.3, Vite 6.3.5, Vitest 3.2.4,
Playwright 1.54.1, Testing Library React 16.3.0, and Vite React plugin 4.6.0.

## Evidence

- `uv sync --locked` completed with CPython 3.12.14.
- Direct Python imports, FastAPI `GET /api/health`, and SQLite foreign-key,
  WAL, and 5,000 ms busy-timeout assertions passed.
- The React Flow and MapLibre smoke canvas test passed under Node 22.
- `npm run build` completed successfully with Vite 6.3.5.
- Docker image build completed with Docker 29.7.2 and the container health
  check returned HTTP 200 from `/api/health`.

The Vite build warns that the initial MapLibre bundle exceeds 500 kB after
minification. This is non-blocking for Gate A0; code splitting is considered
only when real UI modules are introduced.

## Historical A0 completion

These checks were complete when this record was written. Re-run relevant checks
before relying on this as current evidence.
