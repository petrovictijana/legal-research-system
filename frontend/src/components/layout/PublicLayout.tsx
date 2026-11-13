import { Outlet } from 'react-router-dom';
import { SiteHeader } from './SiteHeader';
import styles from '../../App.module.css';

/**
 * Public shell: the SiteHeader + centred content column. The app is now
 * chatbot-only, so there are no navigation items (the header shows just the
 * wordmark + tagline) and no footer. The admin area deliberately does NOT use
 * this layout (it has its own header), so admin routes live outside it.
 */
export function PublicLayout() {
  return (
    <>
      <SiteHeader navItems={[]} />
      <main className={styles.main}>
        <div className={styles.container}>
          <Outlet />
        </div>
      </main>
    </>
  );
}
