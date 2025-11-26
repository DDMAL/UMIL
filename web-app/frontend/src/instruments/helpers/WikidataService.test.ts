import { WikidataService } from './WikidataService';

describe('WikidataService', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('checkIfNameExists', () => {
    it('should return exists true when name found', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          results: {
            bindings: [{ nameLabel: { value: 'Guitar' } }],
          },
        }),
      });

      const result = await WikidataService.checkIfNameExists(
        'Q6607',
        'en',
        'guitar',
      );
      expect(result.exists).toBe(true);
      expect(result.name).toBe('Guitar');
    });

    it('should return exists false when name not found', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          results: {
            bindings: [] as any[],
          },
        }),
      });

      const result = await WikidataService.checkIfNameExists(
        'Q6607',
        'en',
        'unknown',
      );
      expect(result.exists).toBe(false);
    });

    it('should throw error on network failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(
        WikidataService.checkIfNameExists('Q6607', 'en', 'guitar'),
      ).rejects.toThrow('Wikidata query failed');
    });

    it('should throw error on HTTP error', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      });

      await expect(
        WikidataService.checkIfNameExists('Q6607', 'en', 'guitar'),
      ).rejects.toThrow('Wikidata query failed');
    });
  });

  describe('checkIfAlias', () => {
    it('should return exists true when label found', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          results: {
            bindings: [{ nameLabel: { value: 'Guitar' } }],
          },
        }),
      });

      const result = await WikidataService.checkIfAlias('Q6607', 'en');
      expect(result.exists).toBe(true);
      expect(result.name).toBe('Guitar');
    });

    it('should return exists false when label not found', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          results: {
            bindings: [] as any[],
          },
        }),
      });

      const result = await WikidataService.checkIfAlias('Q6607', 'en');
      expect(result.exists).toBe(false);
    });

    it('should throw error on network failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(WikidataService.checkIfAlias('Q6607', 'en')).rejects.toThrow(
        'Wikidata query failed',
      );
    });
  });

  describe('URL construction', () => {
    it('should call correct Wikidata endpoint', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ results: { bindings: [] as any[] } }),
      });
      global.fetch = mockFetch;

      await WikidataService.checkIfNameExists('Q6607', 'en', 'guitar');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('https://query.wikidata.org/sparql'),
      );
    });

    it('should include encoded query and format in URL', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ results: { bindings: [] as any[] } }),
      });
      global.fetch = mockFetch;

      await WikidataService.checkIfNameExists('Q6607', 'en', 'guitar');

      const calledUrl = mockFetch.mock.calls[0][0];
      expect(calledUrl).toContain('query=');
      expect(calledUrl).toContain('format=json');
    });
  });
});
