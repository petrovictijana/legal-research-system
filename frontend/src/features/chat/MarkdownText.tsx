import type { ReactNode } from 'react';
import styles from './MarkdownText.module.css';

/**
 * Renders the subset of Markdown that the RAG answers use:
 * **bold**, *italic*, `code`, #–###### headings, "- " bullets,
 * "1. " numbered lists, and blank-line-separated paragraphs.
 * Deliberately dependency-free so the Apps build stays as-is.
 */

const INLINE_PATTERN = /(\*\*(.+?)\*\*)|(\*(.+?)\*)|(`([^`]+)`)/g;

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let lastIndex = 0;
  let matchIndex = 0;
  INLINE_PATTERN.lastIndex = 0;
  let match = INLINE_PATTERN.exec(text);
  while (match) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    if (match[2] !== undefined) {
      nodes.push(
        <strong key={`${keyPrefix}-b-${matchIndex}`}>{match[2]}</strong>,
      );
    } else if (match[4] !== undefined) {
      nodes.push(<em key={`${keyPrefix}-i-${matchIndex}`}>{match[4]}</em>);
    } else if (match[6] !== undefined) {
      nodes.push(
        <code key={`${keyPrefix}-c-${matchIndex}`} className={styles.code}>
          {match[6]}
        </code>,
      );
    }
    lastIndex = match.index + match[0].length;
    matchIndex += 1;
    match = INLINE_PATTERN.exec(text);
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }
  return nodes;
}

type Block =
  | { kind: 'paragraph'; text: string }
  | { kind: 'heading'; level: number; text: string }
  | { kind: 'bulletList'; items: string[] }
  | { kind: 'orderedList'; items: string[] };

function parseBlocks(content: string): Block[] {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  let bullets: string[] = [];
  let ordered: string[] = [];

  const flushParagraph = () => {
    if (paragraph.length > 0) {
      blocks.push({ kind: 'paragraph', text: paragraph.join(' ') });
      paragraph = [];
    }
  };
  const flushBullets = () => {
    if (bullets.length > 0) {
      blocks.push({ kind: 'bulletList', items: bullets });
      bullets = [];
    }
  };
  const flushOrdered = () => {
    if (ordered.length > 0) {
      blocks.push({ kind: 'orderedList', items: ordered });
      ordered = [];
    }
  };
  const flushAll = () => {
    flushParagraph();
    flushBullets();
    flushOrdered();
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.trim().length === 0) {
      flushAll();
      continue;
    }

    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      flushAll();
      blocks.push({
        kind: 'heading',
        level: heading[1].length,
        text: heading[2].trim(),
      });
      continue;
    }

    const bullet = /^[-*]\s+(.*)$/.exec(line);
    if (bullet) {
      flushParagraph();
      flushOrdered();
      bullets.push(bullet[1].trim());
      continue;
    }

    const orderedItem = /^\d+[.)]\s+(.*)$/.exec(line);
    if (orderedItem) {
      flushParagraph();
      flushBullets();
      ordered.push(orderedItem[1].trim());
      continue;
    }

    flushBullets();
    flushOrdered();
    paragraph.push(line.trim());
  }
  flushAll();
  return blocks;
}

function headingTagFor(level: number): 'h3' | 'h4' {
  return level <= 3 ? 'h3' : 'h4';
}

export interface MarkdownTextProps {
  content: string;
}

export function MarkdownText({ content }: MarkdownTextProps) {
  const blocks = parseBlocks(content);
  return (
    <div className={styles.body}>
      {blocks.map((block, index) => {
        const keyPrefix = `${index}`;
        switch (block.kind) {
          case 'heading': {
            const Heading = headingTagFor(block.level);
            return (
              <Heading key={keyPrefix} className={styles.heading}>
                {renderInline(block.text, keyPrefix)}
              </Heading>
            );
          }
          case 'bulletList':
            return (
              <ul key={keyPrefix} className={styles.list}>
                {block.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    {renderInline(item, `${keyPrefix}-${itemIndex}`)}
                  </li>
                ))}
              </ul>
            );
          case 'orderedList':
            return (
              <ol key={keyPrefix} className={styles.list}>
                {block.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    {renderInline(item, `${keyPrefix}-${itemIndex}`)}
                  </li>
                ))}
              </ol>
            );
          case 'paragraph':
          default:
            return (
              <p key={keyPrefix} className={styles.paragraph}>
                {renderInline(block.text, keyPrefix)}
              </p>
            );
        }
      })}
    </div>
  );
}

