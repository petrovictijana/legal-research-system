import { useCallback, useRef, useState } from 'react';
import type { AskService } from '../../api/ask';
import type { ChatMessageModel, ChatStatus } from './types';

let idCounter = 0;
function nextId(prefix: string): string {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

export interface UseChatResult {
  messages: ChatMessageModel[];
  status: ChatStatus;
  send: (text: string) => void;
  retry: () => void;
}

/**
 * Owns the conversation state and talks to an {@link AskService}. Presentation
 * components stay free of transport concerns. Prevents double submit by
 * ignoring new sends while a request is in flight.
 */
export function useChat(service: AskService): UseChatResult {
  const [messages, setMessages] = useState<ChatMessageModel[]>([]);
  const [status, setStatus] = useState<ChatStatus>('idle');
  const inFlight = useRef(false);
  const lastQuestion = useRef<string | null>(null);

  const run = useCallback(
    (question: string) => {
      if (inFlight.current) return;
      inFlight.current = true;
      lastQuestion.current = question;

      const pendingId = nextId('assistant');
      setStatus('loading');
      setMessages((prev) => [
        ...prev,
        {
          id: pendingId,
          role: 'assistant',
          content: '',
          status: 'pending',
        },
      ]);

      service
        .ask(question)
        .then((response) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === pendingId
                ? {
                    ...message,
                    content: response.answer,
                    sources: response.sources,
                    isMock: response.isMock,
                    status: 'done',
                  }
                : message,
            ),
          );
          setStatus('idle');
        })
        .catch(() => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === pendingId
                ? { ...message, status: 'error' }
                : message,
            ),
          );
          setStatus('error');
        })
        .finally(() => {
          inFlight.current = false;
        });
    },
    [service],
  );

  const send = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || inFlight.current) return;

      setMessages((prev) => [
        ...prev,
        {
          id: nextId('user'),
          role: 'user',
          content: trimmed,
          status: 'done',
        },
      ]);
      run(trimmed);
    },
    [run],
  );

  const retry = useCallback(() => {
    if (inFlight.current) return;
    const question = lastQuestion.current;
    if (!question) return;

    // Drop the failed pending/assistant row before retrying.
    setMessages((prev) => {
      const next = [...prev];
      for (let i = next.length - 1; i >= 0; i -= 1) {
        if (next[i].role === 'assistant' && next[i].status === 'error') {
          next.splice(i, 1);
          break;
        }
      }
      return next;
    });
    run(question);
  }, [run]);

  return { messages, status, send, retry };
}
