import { describe, expect, it, vi } from 'vitest';
import { act, renderHook, waitFor } from '@testing-library/react';
import { useChat } from './useChat';
import type { AskResponse, AskService } from '../../api/ask';

function resolvingService(response: AskResponse): AskService {
  return { ask: vi.fn().mockResolvedValue(response) };
}

function rejectingService(): AskService {
  return { ask: vi.fn().mockRejectedValue(new Error('fail')) };
}

const mockResponse: AskResponse = {
  answer: 'Demo',
  sources: [],
  isMock: true,
};

describe('useChat', () => {
  it('ignores empty / whitespace sends', () => {
    const service = resolvingService(mockResponse);
    const { result } = renderHook(() => useChat(service));
    act(() => result.current.send('   '));
    expect(result.current.messages).toHaveLength(0);
    expect(service.ask).not.toHaveBeenCalled();
  });

  it('appends a user message then a resolved assistant answer', async () => {
    const service = resolvingService(mockResponse);
    const { result } = renderHook(() => useChat(service));

    act(() => result.current.send('Pitanje?'));

    // User + pending assistant immediately.
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toMatchObject({
      role: 'user',
      content: 'Pitanje?',
    });
    expect(result.current.messages[1].status).toBe('pending');

    await waitFor(() =>
      expect(result.current.messages[1].status).toBe('done'),
    );
    expect(result.current.messages[1]).toMatchObject({
      role: 'assistant',
      content: 'Demo',
      isMock: true,
    });
    expect(result.current.status).toBe('idle');
    expect(service.ask).toHaveBeenCalledWith('Pitanje?');
  });

  it('prevents double submit while a request is in flight', async () => {
    const service = resolvingService(mockResponse);
    const { result } = renderHook(() => useChat(service));
    act(() => {
      result.current.send('Prvo');
      result.current.send('Drugo');
    });
    // Only the first send is accepted while in flight.
    expect(service.ask).toHaveBeenCalledTimes(1);
    expect(result.current.messages.filter((m) => m.role === 'user')).toHaveLength(
      1,
    );
    await waitFor(() => expect(result.current.status).toBe('idle'));
  });

  it('sets an error status and supports retry that re-sends the last question', async () => {
    const service = rejectingService();
    const { result } = renderHook(() => useChat(service));

    act(() => result.current.send('Pitanje?'));
    await waitFor(() => expect(result.current.status).toBe('error'));
    expect(
      result.current.messages.some(
        (m) => m.role === 'assistant' && m.status === 'error',
      ),
    ).toBe(true);

    act(() => result.current.retry());
    expect(service.ask).toHaveBeenCalledTimes(2);
    expect(service.ask).toHaveBeenLastCalledWith('Pitanje?');
    await waitFor(() => expect(result.current.status).toBe('error'));
  });
});
