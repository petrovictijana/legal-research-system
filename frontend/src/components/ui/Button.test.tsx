import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders a real button that fires onClick', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Pošalji</Button>);
    const button = screen.getByRole('button', { name: 'Pošalji' });
    await user.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled and busy while loading', () => {
    render(<Button loading>Pošalji</Button>);
    const button = screen.getByRole('button', { name: 'Pošalji' });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('defaults to type="button"', () => {
    render(<Button>Pošalji</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });
});
