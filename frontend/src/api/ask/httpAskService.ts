/**
 * REAL HTTP client for the AI-assisted legal Q&A, backed by the FastAPI
 * Pravnislav API: `POST /api/v1/chat`.
 *
 * Request: `{ question }`. Response: `{ answer, sources }`. Sources are mapped
 * defensively: entries missing a document title are skipped, and
 * `article_number` (which may arrive as a number) is coerced to string, so
 * the UI never renders fabricated citations.
 */

import { CHAT_API_BASE_URL } from '../config';
import type { AskResponse, AskService, AskSource } from './types';

/** The backend's `ChatResponse`; every field may be absent. */
interface ChatResponseBody {
  answer?: string;
  sources?: unknown;
}

/** Normalize the backend's `sources` into {@link AskSource} entries. */
function mapSources(raw: unknown): AskSource[] {
  if (!Array.isArray(raw)) return [];

  return raw.flatMap((item) => {
    if (typeof item !== 'object' || item === null) return [];
    const { document_title: title, article_number: article } = item as Record<
      string,
      unknown
    >;
    if (typeof title !== 'string' || !title) return [];
    return [
      {
        document_title: title,
        article_number: article == null ? '' : String(article),
      },
    ];
  });
}

/**
 * Builds a real ask service bound to `baseUrl`. Exported so tests can point it at
 * a stub origin; the app uses the default {@link httpAskService}.
 */
export function createHttpAskService(baseUrl: string = CHAT_API_BASE_URL): AskService {
  const chatUrl = `${baseUrl.replace(/\/+$/, '')}/api/v1/chat`;

  return {
    async ask(question: string): Promise<AskResponse> {
      let response: Response;
      try {
        response = await fetch(chatUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question }),
        });
      } catch {
        throw new Error('chatbot_network_error');
      }

      if (!response.ok) {
        throw new Error(`chatbot_http_${response.status}`);
      }

      const data = (await response.json()) as ChatResponseBody;
      return {
        answer: data.answer ?? '',
        sources: mapSources(data.sources),
        isMock: false,
      };
    },
  };
}

/** Default real ask service used by the chat panel. */
export const httpAskService: AskService = createHttpAskService();
