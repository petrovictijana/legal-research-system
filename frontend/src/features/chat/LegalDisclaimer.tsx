import { useId, useState } from 'react';
import { InfoIcon } from '../../components/ui/icons';
import { sr } from '../../messages/sr';
import styles from './LegalDisclaimer.module.css';

/**
 * AI-answer disclaimer shown beneath the composer. The "Saznajte više" control
 * is a real disclosure toggle that reveals more detail inline — no backend
 * route is invented, and the AI/legal-source distinction stays perceivable to
 * assistive tech (text + info icon, not colour alone).
 */
export function LegalDisclaimer() {
  const [open, setOpen] = useState(false);
  const detailsId = useId();

  return (
    <div className={styles.wrap}>
      <p className={styles.line}>
        <InfoIcon className={styles.icon} size={16} />
        <span>
          {sr.disclaimer.ai}{' '}
          <button
            type="button"
            className={styles.toggle}
            aria-expanded={open}
            aria-controls={detailsId}
            onClick={() => setOpen((prev) => !prev)}
          >
            {open ? sr.disclaimer.learnMoreHide : sr.disclaimer.learnMore}
          </button>
        </span>
      </p>

      {open && (
        <p id={detailsId} className={styles.details}>
          {sr.disclaimer.aiDetails}
        </p>
      )}
    </div>
  );
}
