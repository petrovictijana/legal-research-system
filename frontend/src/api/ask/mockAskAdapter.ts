import { sr } from '../../messages/sr';
import type { AskResponse, AskService } from './types';

/**
 * MOCK adapter — NO network. Returns `isMock: true` and no sources. Used in
 * tests and before the backend is reachable (e.g. offline development).
 */

const MIN_DELAY_MS = 600;
const MAX_DELAY_MS = 900;

function randomDelay(): number {
  return MIN_DELAY_MS + Math.random() * (MAX_DELAY_MS - MIN_DELAY_MS);
}

export interface MockAskAdapterOptions {
  /** Force a rejection — used in tests to exercise the error path. */
  shouldFail?: boolean;
  /** Override the delay (ms); omit for the natural 600–900ms range. */
  delayMs?: number;
}

export function createMockAskAdapter(
  options: MockAskAdapterOptions = {},
): AskService {
  return {
    // The mock ignores the question; a narrower signature is assignable to AskService.
    ask(): Promise<AskResponse> {
      const delay = options.delayMs ?? randomDelay();
      return new Promise<AskResponse>((resolve, reject) => {
        setTimeout(() => {
          if (options.shouldFail) {
            reject(new Error('mock_ask_failure'));
            return;
          }
          resolve({
            answer: sr.mockAnswer,
            sources: [],
            isMock: true,
          });
        }, delay);
      });
    },
  };
}

/** Default mock service instance used by the app. */
export const mockAskAdapter: AskService = createMockAskAdapter();
