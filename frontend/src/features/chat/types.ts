import type { AskSource } from '../../api/ask';

export type ChatRole = 'user' | 'assistant';
export type MessageStatus = 'pending' | 'done' | 'error';

export interface ChatMessageModel {
  id: string;
  role: ChatRole;
  content: string;
  /** Legal citations for assistant answers; absent for user messages. */
  sources?: AskSource[];
  isMock?: boolean;
  status?: MessageStatus;
}

export type ChatStatus = 'idle' | 'loading' | 'error';
