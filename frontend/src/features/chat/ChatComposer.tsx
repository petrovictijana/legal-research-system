import { forwardRef, useId } from 'react';
import type { ChangeEvent, KeyboardEvent } from 'react';
import { ArrowRightIcon, SparkleIcon } from '../../components/ui/icons';
import { sr } from '../../messages/sr';
import styles from './ChatComposer.module.css';

export interface ChatComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  error?: string;
}

export const ChatComposer = forwardRef<HTMLTextAreaElement, ChatComposerProps>(
  function ChatComposer({ value, onChange, onSubmit, disabled = false, error }, ref) {
    const labelId = useId();
    const helperId = useId();
    const errorId = useId();

    const hasError = Boolean(error);
    const describedBy = [helperId, hasError ? errorId : null]
      .filter(Boolean)
      .join(' ');

    function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
      // Auto-grow up to the CSS max-height, then the textarea scrolls.
      const el = event.target;
      el.style.height = 'auto';
      el.style.height = `${el.scrollHeight}px`;
      onChange(el.value);
    }

    function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        onSubmit();
      }
    }

    return (
      <form
        className={styles.composer}
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        noValidate
      >
        <label id={labelId} htmlFor={`${labelId}-input`} className="visuallyHidden">
          {sr.composer.label}
        </label>
        <div className={styles.row}>
          <SparkleIcon className={styles.leadIcon} size={20} />
          <textarea
            ref={ref}
            id={`${labelId}-input`}
            className={styles.textarea}
            value={value}
            placeholder={sr.composer.placeholder}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            rows={1}
            aria-describedby={describedBy}
            aria-invalid={hasError || undefined}
          />
          <button
            type="submit"
            className={styles.send}
            disabled={disabled}
            aria-label={sr.composer.submitAccessibleName}
          >
            <ArrowRightIcon size={20} />
          </button>
        </div>
        <p id={helperId} className="visuallyHidden">
          {sr.composer.helper}
        </p>
        {hasError && (
          <p id={errorId} className={styles.error} role="alert">
            {error}
          </p>
        )}
      </form>
    );
  },
);
