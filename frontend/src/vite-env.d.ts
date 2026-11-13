/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * Base URL of the Pravnislav backend (the `diplomski-be` Spring Boot service).
   * Defaults to `http://localhost:8080` when unset — the dev server's address,
   * which the backend's CORS config already allows for the Vite origin.
   */
  readonly VITE_API_BASE_URL?: string;

  /**
   * Base URL of the chat backend — the FastAPI Pravdan API exposing
   * `POST /api/v1/chat`. Defaults to `http://localhost:8000` when unset (the
   * local FastAPI dev server). Separate from {@link VITE_API_BASE_URL} because
   * chat and documents are served by different services.
   */
  readonly VITE_CHAT_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
