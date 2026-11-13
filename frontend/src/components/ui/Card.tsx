import type { ElementType, ReactNode } from 'react';
import styles from './Card.module.css';

export interface CardProps {
  as?: ElementType;
  padding?: 'md' | 'lg';
  className?: string;
  children: ReactNode;
}

export function Card({
  as: Tag = 'div',
  padding = 'md',
  className,
  children,
}: CardProps) {
  const classes = [styles.card, styles[padding], className ?? '']
    .filter(Boolean)
    .join(' ');
  return <Tag className={classes}>{children}</Tag>;
}
