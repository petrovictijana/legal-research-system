import type { ChatMessageModel } from './types';
import { AnswerCard } from './AnswerCard';
import styles from './ChatMessage.module.css';

export interface ChatMessageProps {
  message: ChatMessageModel;
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.role === 'user') {
    return (
      <div className={styles.userRow}>
        <div className={styles.userBubble}>{message.content}</div>
      </div>
    );
  }

  return (
    <div className={styles.assistantRow}>
      <AnswerCard
        content={message.content}
        sources={message.sources}
        isMock={message.isMock}
      />
    </div>
  );
}
