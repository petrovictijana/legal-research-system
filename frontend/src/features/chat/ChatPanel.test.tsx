import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatPanel } from './ChatPanel';
import { createMockAskAdapter } from '../../api/ask';
import { sr } from '../../messages/sr';

describe('ChatPanel', () => {
  it('shows the intro with the H1 title and the four example cards on first load', () => {
    render(<ChatPanel service={createMockAskAdapter({ delayMs: 0 })} />);
    expect(
      screen.getByRole('heading', { level: 1, name: sr.hero.title }),
    ).toBeInTheDocument();
    expect(screen.queryByRole('log')).not.toBeInTheDocument();
    const region = screen.getByRole('region', {
      name: sr.examples.heading,
    });
    expect(within(region).getAllByRole('button')).toHaveLength(4);
  });

  it('populates the composer with the question and focuses the textarea when a chip is chosen', async () => {
    const user = userEvent.setup();
    render(<ChatPanel service={createMockAskAdapter({ delayMs: 0 })} />);
    const prompt = sr.examples.prompts[0];
    const chip = screen.getByRole('button', { name: prompt.question });
    await user.click(chip);
    const textarea = screen.getByRole('textbox', { name: sr.composer.label });
    expect((textarea as HTMLTextAreaElement).value).toBe(prompt.question);
    expect(textarea).toHaveFocus();
  });

  it('sends a question and renders the AI answer with the mock notice', async () => {
    const user = userEvent.setup();
    render(<ChatPanel service={createMockAskAdapter({ delayMs: 0 })} />);
    const textarea = screen.getByRole('textbox', { name: sr.composer.label });
    await user.type(textarea, 'Moje pitanje?');
    await user.click(
      screen.getByRole('button', { name: sr.composer.submitAccessibleName }),
    );

    // User message appears in the log.
    const log = await screen.findByRole('log');
    expect(within(log).getByText('Moje pitanje?')).toBeInTheDocument();

    // Assistant answer resolves.
    expect(await screen.findByText(sr.chat.aiBadge)).toBeInTheDocument();
    expect(screen.getByText(sr.chat.mockNotice)).toBeInTheDocument();
  });
});
