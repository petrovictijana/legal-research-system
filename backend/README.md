# Pravnislav API (FastAPI backend)

REST API facade over the existing Databricks RAG pipeline for **Pravnislav**, a
Serbian legal Q&A assistant. This layer does **not** implement retrieval,
embedding, context construction or generation — it calls the existing
`orchestration.query_pipeline.generate_answer`, exactly as the Streamlit app
(`databricks/app.py`) does.

## Endpoints

| Method | Path            | Purpose                                   |
|--------|-----------------|-------------------------------------------|
| GET    | `/health`       | Liveness (no Databricks needed)           |
| POST   | `/api/v1/chat`  | Ask a legal question → answer + sources   |

### `POST /api/v1/chat`

Request:
```json
{ "question": "Који су услови за закључење уговора о раду?" }
```
Response:
```json
{
  "answer": "Уговор о раду закључује се...",
  "sources": [{ "document_title": "Закон о раду", "article_number": "30" }]
}
```
Errors: invalid/empty question → `422`; RAG pipeline failure → `503` with a safe
Serbian Cyrillic message (technical details are logged server-side only).

## Project layout

```
backend/
├── main.py               # FastAPI app: metadata, CORS, router
├── app.yaml              # Databricks Apps startup config
├── requirements.txt      # runtime deps (fastapi, uvicorn, pydantic[-settings])
├── requirements-dev.txt  # + pytest, httpx
├── api/
│   ├── router.py         # mounts /health and /api/v1/*
│   └── routes/{health,chat}.py
├── schemas/chat.py       # ChatRequest, Source, ChatResponse
├── services/chat_service.py   # business logic; maps RAG result → ChatResponse
├── dependencies/rag.py   # in-process access to orchestration.query_pipeline
├── core/settings.py      # centralized config (pydantic-settings)
└── tests/                # pytest + FastAPI TestClient (RAG mocked)
```

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # optional; adjust CORS / environment
uvicorn main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs (development only)

> The `orchestration` package is **not** present locally — it lives in the
> Databricks workspace. Locally, `/health` and request validation work, and
> `/api/v1/chat` returns `503` (the import fails, logged server-side). This is
> expected. To exercise the full chat path locally, put an importable
> `orchestration/query_pipeline.py` exposing
> `generate_answer(query=...) -> {"answer", "sources"}` on `PYTHONPATH`.

## Tests

```bash
source .venv/bin/activate
pytest
```
Tests mock the RAG pipeline (`dependencies.rag.get_rag_runner` override), so no
Databricks connection is required. Covered: route registration, health,
request validation (empty/whitespace/too-long), successful chat with mocked RAG,
source mapping (incl. numeric `article_number` coercion and skipping malformed
sources), RAG-failure → safe `503`, and response-schema shape.

## Deploy on Databricks Apps

1. Deploy this `backend/` where the `orchestration` package is importable
   (i.e. alongside it in the Databricks RAG repo), so
   `from orchestration.query_pipeline import generate_answer` resolves.
2. `app.yaml` is the startup config. Databricks Apps injects the port via the
   `DATABRICKS_APP_PORT` env var (the only variable expandable inside
   `command`), and the app binds to it. Do **not** hard-code `8080` — that port
   is not forwarded.
3. `fastapi`/`uvicorn` exist in the base Apps environment; `requirements.txt`
   lists them so local/CI runs match. Databricks (Vector Search, LLM, auth)
   dependencies are intentionally **not** duplicated here — the pipeline owns
   them.
4. Databricks authentication is handled by the existing pipeline / the app's
   service principal. This backend adds **no** tokens and reads **no** secrets.

## Configuration

Environment variables, prefixed `PRAVNISLAV_` (see `.env.example`):

| Variable                      | Default                   | Meaning                              |
|-------------------------------|---------------------------|--------------------------------------|
| `PRAVNISLAV_ENVIRONMENT`         | `development`             | `development` enables `/docs`        |
| `PRAVNISLAV_CORS_ALLOW_ORIGINS`  | `http://localhost:5173`   | CSV or JSON array of allowed origins |

## Connecting the React frontend (`pravnislav-fe`)

The frontend currently calls `POST /chatbot` and reads only `answer`. To use
this backend, it needs:

- Base URL → this service (`VITE_API_BASE_URL`), and the path changed from
  `/chatbot` to `/api/v1/chat` (`src/api/ask/httpAskService.ts`).
- Add this backend's origin to `PRAVNISLAV_CORS_ALLOW_ORIGINS`.
- Optionally re-enable source rendering (the FE currently ignores `sources`).
