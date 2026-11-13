import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AnswerCard } from './AnswerCard';
import { sr } from '../../messages/sr';

describe('AnswerCard', () => {
  it('renders the AI badge, body, disclaimer and mock notice (no sources)', () => {
    render(<AnswerCard content="Telo odgovora" isMock />);

    expect(screen.getByText(sr.chat.aiBadge)).toBeInTheDocument();
    expect(screen.getByText('Telo odgovora')).toBeInTheDocument();
    expect(screen.getByText(sr.chat.aiDisclaimer)).toBeInTheDocument();
    expect(screen.getByText(sr.chat.mockNotice)).toBeInTheDocument();
  });

  it('does not render a sources section', () => {
    render(<AnswerCard content="Telo" isMock={false} />);
    expect(screen.queryByText('Izvori')).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 2 })).not.toBeInTheDocument();
  });

  it('does not render the mock notice when isMock is false', () => {
    render(<AnswerCard content="Telo" isMock={false} />);
    expect(screen.queryByText(sr.chat.mockNotice)).not.toBeInTheDocument();
  });
});
