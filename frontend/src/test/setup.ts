import '@testing-library/jest-dom';
import { vi } from 'vitest';

// jsdom does not implement scrollIntoView; provide a no-op so auto-scroll works.
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = vi.fn();
}
