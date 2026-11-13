/**
 * Shared API configuration for the real HTTP layer.
 *
 * This is the single source of truth for where the backend lives. Individual
 * API clients build their URLs from {@link API_BASE_URL}; they never hard-code a
 * host. Override it per environment with the `VITE_API_BASE_URL` build-time env
 * var (see `src/vite-env.d.ts`).
 *
 * The default targets the local `diplomski-be` Spring Boot service on port 8080,
 * whose CORS config allows the Vite dev origin (`http://localhost:5173`).
 */
export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080'
).replace(/\/+$/, '');

/**
 * Base URL of the **chat** backend — the FastAPI Pravnislav API that exposes
 * `POST /api/v1/chat`. In production (Databricks Apps) the built frontend is
 * served by that same FastAPI process, so the default is same-origin (an
 * empty string → relative URL, no CORS). For local development against a
 * separate Vite dev server, set `VITE_CHAT_API_BASE_URL` (e.g.
 * `http://localhost:8000`).
 */
export const CHAT_API_BASE_URL: string = (
  import.meta.env.VITE_CHAT_API_BASE_URL ?? ''
).replace(/\/+$/, '');
