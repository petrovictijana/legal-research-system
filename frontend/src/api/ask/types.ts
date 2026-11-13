/**
 * API/domain contract for the AI-assisted legal Q&A.
 *
 * Mirrors the FastAPI backend's `ChatResponse` (POST /api/v1/chat). Fields the
 * backend may omit are optional at the transport boundary, but the HTTP
 * adapter normalizes them so the UI never has to handle absent keys.
 */

/** A single legal citation backing an answer (backend `Source`). */
export interface AskSource {
  document_title: string;
  article_number: string;
}

/** Response shape returned by an {@link AskService}. */
export interface AskResponse {
  answer: string;
  /** Legal sources the answer is grounded in; empty when none. */
  sources: AskSource[];
  /** True when the answer comes from a mock adapter, not a real legal base. */
  isMock: boolean;
}

/** Transport-agnostic service for asking a legal question. */
export interface AskService {
  ask(question: string): Promise<AskResponse>;
}
