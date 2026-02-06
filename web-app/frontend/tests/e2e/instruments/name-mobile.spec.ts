import { test, expect } from '../../fixtures/pages';
import { test as authTest } from '../../fixtures/auth';
import { TEST_INSTRUMENT } from '../../constants/testData';

test.describe('Add Name - Mobile', () => {
  authTest(
    'should add single name to instrument',
    async ({ instrumentDetailPage }) => {
      await instrumentDetailPage.goto(TEST_INSTRUMENT);

      const timestamp = Date.now();
      const testName = `Test Name ${timestamp}`;

      // Add name (page object handles mobile differences)
      await instrumentDetailPage.addName('fr', testName);

      // Wait for name to appear in table
      await expect(
        instrumentDetailPage.hasName('French', testName),
      ).resolves.toBe(true);
    },
  );

  authTest(
    'should add multiple names in same language',
    async ({ instrumentDetailPage }) => {
      await instrumentDetailPage.goto(TEST_INSTRUMENT);

      const timestamp = Date.now();
      const name1 = `Test Name 1 ${timestamp}`;
      const name2 = `Test Name 2 ${timestamp}`;

      // Add first name
      await instrumentDetailPage.addName('de', name1);
      await expect(instrumentDetailPage.hasName('German', name1)).resolves.toBe(
        true,
      );

      // Add second name in same language
      await instrumentDetailPage.addName('de', name2);
      await expect(instrumentDetailPage.hasName('German', name2)).resolves.toBe(
        true,
      );

      // Verify both names appear
      const hasName1 = await instrumentDetailPage.hasName('German', name1);
      const hasName2 = await instrumentDetailPage.hasName('German', name2);

      expect(hasName1).toBe(true);
      expect(hasName2).toBe(true);
    },
  );

  test('should not show add button when not authenticated', async ({
    instrumentDetailPage,
  }) => {
    await instrumentDetailPage.goto(TEST_INSTRUMENT);
    await expect(instrumentDetailPage.getAddNameButton()).not.toBeVisible();
  });

  authTest(
    'should show add button after login',
    async ({ instrumentDetailPage }) => {
      await instrumentDetailPage.goto(TEST_INSTRUMENT);
      await expect(instrumentDetailPage.getAddNameButton()).toBeVisible();
    },
  );
});

test.describe('Delete Name - Mobile', () => {
  authTest(
    'should delete name from instrument',
    async ({ instrumentDetailPage }) => {
      // First add a name we can safely delete
      const timestamp = Date.now();
      const testName = `Test Delete ${timestamp}`;

      await instrumentDetailPage.goto(TEST_INSTRUMENT);
      await instrumentDetailPage.addName('de', testName);
      await expect(
        instrumentDetailPage.hasName('German', testName),
      ).resolves.toBe(true);

      // Get count before deletion
      const countBefore = await instrumentDetailPage.getNameCount();

      // Delete the name
      await instrumentDetailPage.deleteNameByLanguage('German');

      // Wait for deletion to complete by checking count decreased
      await expect(async () => {
        const countAfter = await instrumentDetailPage.getNameCount();
        expect(countAfter).toBe(countBefore - 1);
      }).toPass();

      // Verify name is gone
      const hasName = await instrumentDetailPage.hasName('German', testName);
      expect(hasName).toBe(false);
    },
  );

  test('should not show delete button when not authenticated', async ({
    instrumentDetailPage,
  }) => {
    await instrumentDetailPage.goto(TEST_INSTRUMENT);
    await expect(instrumentDetailPage.get1stActions()).not.toBeVisible();
  });

  authTest(
    'should show delete button for contributor',
    async ({ instrumentDetailPage }) => {
      await instrumentDetailPage.goto(TEST_INSTRUMENT);
      await expect(instrumentDetailPage.get1stActions()).toBeVisible();
    },
  );
});
