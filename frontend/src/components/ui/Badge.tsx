import type { ReactNode } from 'react';
import { SparkleIcon } from './icons';
import styles from './Badge.module.css';

type BadgeVariant = 'ai' | 'neutral';

export interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
}

export function Badge({ variant = 'neutral', children }: BadgeProps) {
  return (
    <span className={[styles.badge, styles[variant]].join(' ')}>
      {variant === 'ai' && <SparkleIcon className={styles.icon} size={14} />}
      <span>{children}</span>
    </span>
  );
}
