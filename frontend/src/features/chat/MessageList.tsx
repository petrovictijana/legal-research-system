import { useEffect, useRef } from 'react';
import { Button } from '../../components/ui/Button';
import { SparkleIcon } from '../../components/ui/icons';
import { sr } from '../../messages/sr';
import { ChatMessage } from './ChatMessage';
import type { ChatMessageModel, ChatStatus } from './types';
import styles from './MessageList.module.css';

export interface MessageListProps {
  messages: ChatMessageModel[];
  status: ChatStatus;
  onRetry: () => void;
}

export function MessageList({ messages, status, onRetry }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to newest; reduced-motion users get an instant jump.
  useEffect(() => {
    const prefersReduced = window.matchMedia?.(
      '(prefers-reduced-motion: reduce)',
    ).matches;
    endRef.current?.scrollIntoView({
      behavior: prefersReduced ? 'auto' : 'smooth',
      block: 'end',
    });
  }, [messages, status]);

  return (
    <div
      className={styles.log}
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      aria-label={sr.brand.wordmark}
    >
      {messages.map((message) => {
        if (message.role === 'assistant' && message.status === 'pending') {
          return (
            <div key={message.id} className={styles.pendingRow}>
              <SparkleIcon className={styles.pendingIcon} size={18} />
              <span className={styles.spinner} aria-hidden="true" />
              <span className={styles.pendingText}>{sr.chat.loading}</span>
            </div>
          );
        }

        if (message.role === 'assistant' && message.status === 'error') {
          return (
            <div key={message.id} className={styles.errorRow} role="alert">
              <p className={styles.errorText}>{sr.chat.error}</p>
              <Button variant="secondary" size="sm" onClick={onRetry}>
                {sr.chat.retry}
              </Button>
            </div>
          );
        }

        return <ChatMessage key={message.id} message={message} />;
      })}
      <div ref={endRef} />
    </div>
  );
}
