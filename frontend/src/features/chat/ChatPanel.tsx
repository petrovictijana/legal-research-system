import { useRef, useState } from 'react';
import type { AskService } from '../../api/ask';
import { httpAskService } from '../../api/ask';
import { sr } from '../../messages/sr';
import { ChatbotHero } from './ChatbotHero';
import { ChatComposer } from './ChatComposer';
import { ExamplePrompts } from './ExamplePrompts';
import { LegalDisclaimer } from './LegalDisclaimer';
import { MessageList } from './MessageList';
import { useChat } from './useChat';
import styles from './ChatPanel.module.css';

export interface ChatPanelProps {
  /** Injectable for tests; defaults to the real `POST /api/v1/chat` HTTP service. */
  service?: AskService;
}

export function ChatPanel({ service = httpAskService }: ChatPanelProps) {
  const { messages, status, send, retry } = useChat(service);
  const [value, setValue] = useState('');
  const [error, setError] = useState<string | undefined>(undefined);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isLoading = status === 'loading';
  const hasConversation = messages.length > 0;

  function handleSubmit() {
    if (isLoading) return;
    if (value.trim().length === 0) {
      setError(sr.composer.validationEmpty);
      textareaRef.current?.focus();
      return;
    }
    setError(undefined);
    send(value);
    setValue('');
    // Reset the auto-grown height.
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }

  function handleChange(next: string) {
    setValue(next);
    if (error && next.trim().length > 0) setError(undefined);
  }

  function handleSelectPrompt(prompt: string) {
    setValue(prompt);
    setError(undefined);
    const el = textareaRef.current;
    if (el) {
      el.focus();
      const end = prompt.length;
      // Caret at end.
      requestAnimationFrame(() => el.setSelectionRange(end, end));
    }
  }

  const composer = (
    <ChatComposer
      ref={textareaRef}
      value={value}
      onChange={handleChange}
      onSubmit={handleSubmit}
      disabled={isLoading}
      error={error}
    />
  );

  if (hasConversation) {
    return (
      <div className={styles.panel}>
        <div className={styles.conversation}>
          <MessageList messages={messages} status={status} onRetry={retry} />
        </div>
        <div className={styles.composerArea}>{composer}</div>
      </div>
    );
  }

  return (
    <div className={styles.panelIntro}>
      <section className={styles.intro}>
        <ChatbotHero />
        <ExamplePrompts
          prompts={sr.examples.prompts}
          onSelect={handleSelectPrompt}
        />
        <div className={styles.introComposer}>
          {composer}
          <LegalDisclaimer />
        </div>
      </section>
    </div>
  );
}
