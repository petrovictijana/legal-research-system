import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExamplePrompts } from './ExamplePrompts';
import { sr } from '../../messages/sr';

describe('ExamplePrompts', () => {
  it('renders every prompt as a real button showing the question text in a labelled section', () => {
    render(<ExamplePrompts prompts={sr.examples.prompts} onSelect={vi.fn()} />);
    const region = screen.getByRole('region', {
      name: sr.examples.heading,
    });
    expect(region).toBeInTheDocument();
    sr.examples.prompts.forEach((prompt) => {
      expect(
        screen.getByRole('button', { name: prompt.question }),
      ).toBeInTheDocument();
    });
  });

  it('calls onSelect with the question when clicked', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(<ExamplePrompts prompts={sr.examples.prompts} onSelect={onSelect} />);
    const first = sr.examples.prompts[0];
    await user.click(screen.getByRole('button', { name: first.question }));
    expect(onSelect).toHaveBeenCalledWith(first.question);
  });
});
