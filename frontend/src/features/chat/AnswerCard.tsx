import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { sr } from '../../messages/sr';
import type { AskSource } from '../../api/ask';
import { MarkdownText } from './MarkdownText';
import styles from './AnswerCard.module.css';

export interface AnswerCardProps {
  content: string;
  /** Legal citations backing the answer; rendered when non-empty. */
  sources?: AskSource[];
  isMock?: boolean;
}

export function AnswerCard({ content, sources = [], isMock }: AnswerCardProps) {
  return (
    <Card as="article" className={styles.card}>
      <div className={styles.badgeRow}>
        <Badge variant="ai">{sr.chat.aiBadge}</Badge>
      </div>

      <MarkdownText content={content} />

      {sources.length > 0 && (
        <div className={styles.sources}>
          <p className={styles.sourcesHeading}>{sr.chat.sourcesHeading}</p>
          <ul className={styles.sourcesList}>
            {sources.map((source) => (
              <li
                key={`${source.document_title}|${source.article_number}`}
                className={styles.sourceItem}
              >
                {source.document_title}
                {source.article_number
                  ? ` — ${sr.chat.articleLabel} ${source.article_number}`
                  : ''}
              </li>
            ))}
          </ul>
        </div>
      )}

      <hr className={styles.rule} />

      <p className={styles.disclaimer}>{sr.chat.aiDisclaimer}</p>

      {isMock && <p className={styles.mockNotice}>{sr.chat.mockNotice}</p>}
    </Card>
  );
}
