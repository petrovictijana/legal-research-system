import { describe, expect, it, vi } from 'vitest';
import { useState } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatComposer } from './ChatComposer';
import { sr } from '../../messages/sr';

function Harness({ onSubmit }: { onSubmit: (value: string) => void }) {
  const [value, setValue] = useState('');
  const [error, setError] = useState<string | undefined>();
  return (
    <ChatComposer
      value={value}
      onChange={setValue}
      onSubmit={() => {
        if (value.trim().length === 0) {
          setError(sr.composer.validationEmpty);
          return;
        }
        setError(undefined);
        onSubmit(value);
      }}
      error={error}
    />
  );
}

describe('ChatComposer', () => {
  it('exposes a bound accessible label and helper text', () => {
    render(<Harness onSubmit={vi.fn()} />);
    const textarea = screen.getByRole('textbox', { name: sr.composer.label });
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAccessibleDescription(
      expect.stringContaining(sr.composer.helper),
    );
  });

  it('keeps the submit button enabled while empty (empty submit is validated instead)', () => {
    render(<Harness onSubmit={vi.fn()} />);
    expect(
      screen.getByRole('button', { name: sr.composer.submitAccessibleName }),
    ).toBeEnabled();
  });

  it('shows a validation error and aria-invalid on empty submit via Enter', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<Harness onSubmit={onSubmit} />);
    const emptyTextarea = screen.getByRole('textbox', {
      name: sr.composer.label,
    });
    emptyTextarea.focus();
    await user.keyboard('{Enter}');
    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent(
      sr.composer.validationEmpty,
    );
    expect(
      screen.getByRole('textbox', { name: sr.composer.label }),
    ).toHaveAttribute('aria-invalid', 'true');
  });

  it('submits on Enter and inserts a newline on Shift+Enter', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<Harness onSubmit={onSubmit} />);
    const textarea = screen.getByRole('textbox', { name: sr.composer.label });

    await user.type(textarea, 'Prva linija');
    await user.keyboard('{Shift>}{Enter}{/Shift}');
    await user.type(textarea, 'Druga linija');
    expect(onSubmit).not.toHaveBeenCalled();
    expect((textarea as HTMLTextAreaElement).value).toContain('\n');

    await user.keyboard('{Enter}');
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });
});
