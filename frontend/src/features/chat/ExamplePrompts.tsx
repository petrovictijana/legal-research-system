import { useId } from 'react';
import type { ComponentType } from 'react';
import { sr } from '../../messages/sr';
import type { IconProps } from '../../components/ui/icons';
import {
  ArrowRightIcon,
  CalendarIcon,
  CarIcon,
  FileTextIcon,
  HomeIcon,
  UsersIcon,
} from '../../components/ui/icons';
import styles from './ExamplePrompts.module.css';

export interface ExamplePrompt {
  id: string;
  question: string;
}

export interface ExamplePromptsProps {
  prompts: readonly ExamplePrompt[];
  /** Receives the full question text. */
  onSelect: (question: string) => void;
}

/** Simple line icon per prompt id. Icons are decorative — text carries meaning. */
const PROMPT_ICON: Record<string, ComponentType<IconProps>> = {
  'godisnji-odmor': CalendarIcon,
  registracija: HomeIcon,
  porodiljsko: UsersIcon,
  'zimske-gume': CarIcon,
};

export function ExamplePrompts({ prompts, onSelect }: ExamplePromptsProps) {
  const headingId = useId();
  return (
    <section aria-labelledby={headingId} className={styles.section}>
      <h2 id={headingId} className={styles.heading}>
        {sr.examples.heading}
      </h2>
      <ul className={styles.grid}>
        {prompts.map((prompt) => {
          const Icon = PROMPT_ICON[prompt.id] ?? FileTextIcon;
          return (
            <li key={prompt.id} className={styles.item}>
              <button
                type="button"
                className={styles.card}
                onClick={() => onSelect(prompt.question)}
              >
                <span className={styles.iconCircle}>
                  <Icon size={18} />
                </span>
                <span className={styles.text}>{prompt.question}</span>
                <ArrowRightIcon className={styles.arrow} size={18} />
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
