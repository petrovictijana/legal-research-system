import { ChatBubbleIcon } from '../../components/ui/icons';
import { sr } from '../../messages/sr';
import styles from './ChatbotHero.module.css';

/**
 * Landing hero: a navy rounded-square icon tile (with small burgundy "spark"
 * accent strokes), the serif title, and a muted supporting subtitle. The title
 * is the document's single <h1>.
 */
export function ChatbotHero() {
  return (
    <div className={styles.hero}>
      <div className={styles.mark}>
        <span className={styles.tile}>
          <ChatBubbleIcon size={24} />
        </span>
        {/* Decorative burgundy spark strokes at the tile's top-right corner. */}
        <svg
          className={styles.sparks}
          viewBox="0 0 24 24"
          aria-hidden="true"
          focusable="false"
        >
          <g
            stroke="var(--color-burgundy)"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <line x1="12" y1="9" x2="16" y2="5" />
            <line x1="16" y1="12" x2="21" y2="11" />
            <line x1="14" y1="11" x2="17" y2="9" />
          </g>
        </svg>
      </div>

      <h1 className={styles.title}>{sr.hero.title}</h1>
      <p className={styles.subtitle}>{sr.hero.subtitle}</p>
    </div>
  );
}
