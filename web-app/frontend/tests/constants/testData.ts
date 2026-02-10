/**
 * Test instrument IDs used across E2E tests.
 * These correspond to fixtures loaded in the test database.
 */
export const TEST_INSTRUMENT = 'UMIL-00001';

/**
 * Test data patterns used for creating temporary test data
 */
export const TEST_PATTERNS = {
  /** Generate unique instrument source */
  instrumentSource: (timestamp: number) => `Test Source ${timestamp}`,

  /** Generate unique instrument name */
  instrumentName: (timestamp: number) => `Test Instrument ${timestamp}`,

  /** Generate unique name for deletion tests */
  deleteName: (timestamp: number) => `Test Delete ${timestamp}`,

  /** Generate unique English name */
  englishName: (timestamp: number) => `English Name ${timestamp}`,

  /** Generate unique French name */
  frenchName: (timestamp: number) => `Nom Français ${timestamp}`,

  /** Generate unique German name */
  germanName: (timestamp: number) => `Deutscher Name ${timestamp}`,
} as const;
