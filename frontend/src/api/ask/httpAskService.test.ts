import { afterEach, describe, expect, it, vi } from 'vitest';
import { createHttpAskService } from './httpAskService';

const BASE = 'http://backend.test';

function okResponse(body: unknown) {
  return vi.fn(async () => ({
    ok: true,
    status: 200,
    json: async () => body,
  }) as Response);
}

describe('httpAskService', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('POSTs { question } to /api/v1/chat and returns the answer (ignoring sources)', async () => {
    const fetchStub = okResponse({
      answer: 'Odgovor na pitanje.',
      sources: ['Zakon o radu', { title: 'Uredba', url: 'http://x' }],
    });
    vi.stubGlobal('fetch', fetchStub);

    const service = createHttpAskService(BASE);
    const res = await service.ask('Koje je radno vreme?');

    expect(fetchStub).toHaveBeenCalledWith(
      'http://backend.test/api/v1/chat',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ question: 'Koje je radno vreme?' }),
      }),
    );
    expect(res.answer).toBe('Odgovor na pitanje.');
    expect(res.isMock).toBe(false);
    expect(res).not.toHaveProperty('citations');
  });

  it('tolerates a missing answer field (empty string)', async () => {
    vi.stubGlobal('fetch', okResponse({ sources: [] }));
    const res = await createHttpAskService(BASE).ask('x');
    expect(res.answer).toBe('');
  });

  it('throws on a non-2xx response (e.g. 503 when the RAG pipeline is down)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({ ok: false, status: 503, json: async () => ({}) }) as Response),
    );
    await expect(createHttpAskService(BASE).ask('x')).rejects.toThrow(/503/);
  });
});
