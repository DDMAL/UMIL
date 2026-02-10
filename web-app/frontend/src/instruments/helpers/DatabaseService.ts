import type { NameEntry } from '../Types';
import { getCsrfToken } from '../../utils/cookies';

interface DuplicateCheckResult {
  language: string;
  name: string;
  exists: boolean;
}

interface DuplicateCheckResponse {
  duplicates: DuplicateCheckResult[];
}

/**
 * Service for checking instrument data against the database.
 * Used for frontend validation to provide immediate feedback.
 */
export class DatabaseService {
  /**
   * Check if multiple instrument names already exist in database.
   * More efficient than individual checks - one API call for all names.
   *
   * @param entries - Array of name entries to check
   * @returns Promise with duplicate check results for each entry
   */
  static async checkDuplicateNames(
    entries: NameEntry[],
  ): Promise<DuplicateCheckResponse> {
    // Filter to only entries with both language and name
    const namesToCheck = entries
      .filter((entry) => entry.language && entry.name)
      .map((entry) => ({
        language: entry.language,
        name: entry.name,
      }));

    if (namesToCheck.length === 0) {
      return { duplicates: [] };
    }

    const response = await fetch('/api/check-instrument-names/', {
      method: 'POST',
      body: JSON.stringify(namesToCheck),
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
    });

    if (!response.ok) {
      throw new Error('Failed to check duplicate names');
    }

    return await response.json();
  }
}
