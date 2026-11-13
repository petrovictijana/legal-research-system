import { useEffect, useId, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { CloseIcon, MenuIcon } from '../ui/icons';
import { sr } from '../../messages/sr';
import styles from './SiteHeader.module.css';

export interface NavItem {
  /** Stable key. */
  key: string;
  label: string;
  /**
   * Target route. A real path (e.g. `/baza-propisa`) renders a navigable link
   * whose active state is driven by the current route. A `#` placeholder has no
   * destination yet and renders as a present-but-inert control.
   */
  to: string;
}

export interface SiteHeaderProps {
  navItems: NavItem[];
}

export function SiteHeader({ navItems }: SiteHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();
  const menuRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);

  // Close on Escape and trap focus while the mobile menu is open.
  useEffect(() => {
    if (!menuOpen) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setMenuOpen(false);
        toggleRef.current?.focus();
        return;
      }
      if (event.key === 'Tab' && menuRef.current) {
        const focusable = menuRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]):not([aria-disabled="true"])',
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (event.shiftKey && active === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && active === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener('keydown', onKeyDown);
    const firstFocusable = menuRef.current?.querySelector<HTMLElement>(
      'a[href], button:not([disabled]):not([aria-disabled="true"])',
    );
    firstFocusable?.focus();

    return () => document.removeEventListener('keydown', onKeyDown);
  }, [menuOpen]);

  function renderNavLinks(onNavigate?: () => void) {
    return navItems.map((item) => {
      // Placeholder items have no destination yet: present-but-inert.
      if (item.to.startsWith('#')) {
        return (
          <button
            key={item.key}
            type="button"
            className={styles.navLink}
            aria-disabled="true"
            onClick={(e) => e.preventDefault()}
          >
            {item.label}
          </button>
        );
      }
      // Real route: NavLink navigates client-side and sets aria-current="page"
      // on the active item automatically. `end` keeps "/" active only at root.
      return (
        <NavLink
          key={item.key}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) =>
            isActive
              ? [styles.navLink, styles.navLinkActive].join(' ')
              : styles.navLink
          }
          onClick={onNavigate}
        >
          {item.label}
        </NavLink>
      );
    });
  }

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <a href="/" className={styles.wordmark}>
          <span className={styles.wordmarkName}>{sr.brand.wordmark}</span>
          <span className={styles.tagline}>{sr.brand.tagline}</span>
        </a>

        {navItems.length > 0 && (
          <nav className={styles.nav} aria-label={sr.nav.label}>
            <div className={styles.deskLinks}>{renderNavLinks()}</div>

            <button
              ref={toggleRef}
              type="button"
              className={styles.menuToggle}
              aria-expanded={menuOpen}
              aria-controls={menuId}
              aria-label={menuOpen ? sr.nav.menuClose : sr.nav.menuOpen}
              onClick={() => setMenuOpen((open) => !open)}
            >
              {menuOpen ? <CloseIcon size={24} /> : <MenuIcon size={24} />}
            </button>

            {menuOpen && (
              <div id={menuId} ref={menuRef} className={styles.mobileMenu}>
                {renderNavLinks(() => setMenuOpen(false))}
              </div>
            )}
          </nav>
        )}
      </div>
    </header>
  );
}
