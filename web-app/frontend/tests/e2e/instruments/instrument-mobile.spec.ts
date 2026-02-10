import { test, expect } from '../../fixtures/pages';
import { test as authTest } from '../../fixtures/auth';
import { InstrumentDetailPage } from '../../pages';
import { TEST_INSTRUMENT, TEST_PATTERNS } from '../../constants/testData';

test.describe('Create Instrument - Mobile', () => {
  authTest(
    'should create instrument with single name',
    async ({ createInstrumentPage, page }) => {
      await createInstrumentPage.goto();

      const timestamp = Date.now();
      await createInstrumentPage.createInstrument({
        instrumentSource: TEST_PATTERNS.instrumentSource(timestamp),
        hbsClass: '321.322',
        names: [
          {
            language: 'en',
            name: TEST_PATTERNS.instrumentName(timestamp),
            source: 'E2E Test',
          },
        ],
      });

      // Wait for redirect to detail page
      await page.waitForURL(/\/instrument\/UMIL-\d+\//);

      // Verify instrument data
      const instrumentDetailPage = new InstrumentDetailPage(page);
      await expect(instrumentDetailPage.getInstrumentName()).toContainText(
        TEST_PATTERNS.instrumentName(timestamp),
      );
    },
  );

  authTest(
    'should create instrument with multiple names',
    async ({ createInstrumentPage, page }) => {
      await createInstrumentPage.goto();

      const timestamp = Date.now();
      await createInstrumentPage.createInstrument({
        instrumentSource: TEST_PATTERNS.instrumentSource(timestamp),
        hbsClass: '123.45',
        names: [
          {
            language: 'en',
            name: TEST_PATTERNS.englishName(timestamp),
            source: 'E2E Test',
          },
          {
            language: 'fr',
            name: TEST_PATTERNS.frenchName(timestamp),
            source: 'E2E Test',
          },
          {
            language: 'de',
            name: TEST_PATTERNS.germanName(timestamp),
            source: 'E2E Test',
          },
        ],
      });

      // Wait for redirect
      await page.waitForURL(/\/instrument\/UMIL-\d+\//);

      // Verify all names appear
      const instrumentDetailPage = new InstrumentDetailPage(page);
      const languageNames = await instrumentDetailPage.getLanguageNames();

      expect(languageNames).toContain('English');
      expect(languageNames).toContain('French');
      expect(languageNames).toContain('German');
    },
  );

  authTest(
    'should require instrument source',
    async ({ createInstrumentPage, page }) => {
      await createInstrumentPage.goto();

      // Fill only HBS class and name, skip instrument source
      await createInstrumentPage.getHBSClassInput().fill('321.322');
      await createInstrumentPage.fillNameRow(0, {
        language: 'en',
        name: 'Test',
        source: 'Test Source',
      });

      // Try to submit
      await createInstrumentPage.getSubmitButton().click();

      // Should not navigate away (validation prevents submission)
      await expect(page).toHaveURL('/instrument/create/');

      // Should show validation error
      await expect(createInstrumentPage.getInstrumentSourceInput()).toHaveClass(
        /is-invalid/,
      );
    },
  );

  authTest(
    'should require valid HBS classification',
    async ({ createInstrumentPage, page }) => {
      await createInstrumentPage.goto();

      const timestamp = Date.now();
      await createInstrumentPage.getInstrumentSourceInput().fill('Test Source');
      await createInstrumentPage.getHBSClassInput().fill('invalid'); // Invalid format
      await createInstrumentPage.fillNameRow(0, {
        language: 'en',
        name: `Test ${timestamp}`,
        source: 'Test',
      });

      // Try to submit
      await createInstrumentPage.getSubmitButton().click();

      // Should not navigate away and show validation error
      await expect(page).toHaveURL('/instrument/create/');
      await expect(createInstrumentPage.getHBSClassInput()).toHaveClass(
        /is-invalid/,
      );
    },
  );

  authTest(
    'should require at least one name',
    async ({ createInstrumentPage, page }) => {
      await createInstrumentPage.goto();

      // Fill only metadata, no names
      await createInstrumentPage.getInstrumentSourceInput().fill('Test Source');
      await createInstrumentPage.getHBSClassInput().fill('321.322');

      // Try to submit
      await createInstrumentPage.getSubmitButton().click();

      // Should not proceed (validation error)
      await expect(page).toHaveURL('/instrument/create/');
    },
  );

  test('should require authentication', async ({
    createInstrumentPage,
    page,
  }) => {
    await createInstrumentPage.goto();

    // Should redirect to login
    await expect(page).toHaveURL(/\/accounts\/login\//);
  });

  authTest(
    'should add and remove name rows dynamically',
    async ({ createInstrumentPage }) => {
      await createInstrumentPage.goto();

      // Initially should have 1 row (default)
      const initialCount = await createInstrumentPage.getNameRowCount();
      expect(initialCount).toBeGreaterThan(0);

      // Add another row
      await createInstrumentPage.getAddRowButton().click();
      await expect(createInstrumentPage.getNameRows()).toHaveCount(
        initialCount + 1,
      );

      const afterAddCount = await createInstrumentPage.getNameRowCount();
      expect(afterAddCount).toBe(initialCount + 1);

      // Remove a row (if there's a remove button)
      if (afterAddCount > 1) {
        await createInstrumentPage.removeNameRow(afterAddCount - 1);
        await expect(createInstrumentPage.getNameRows()).toHaveCount(
          afterAddCount - 1,
        );

        const afterRemoveCount = await createInstrumentPage.getNameRowCount();
        expect(afterRemoveCount).toBe(afterAddCount - 1);
      }
    },
  );
});

test.describe('Delete Instrument - Mobile', () => {
  authTest(
    'should delete user-created instrument',
    async ({
      createInstrumentPage,
      instrumentDetailPage,
      instrumentListPage,
      page,
    }) => {
      // Step 1: Create an instrument
      const timestamp = Date.now();
      await createInstrumentPage.goto();
      await createInstrumentPage.createInstrument({
        instrumentSource: TEST_PATTERNS.instrumentSource(timestamp),
        hbsClass: '321.322',
        names: [
          {
            language: 'en',
            name: TEST_PATTERNS.deleteName(timestamp),
            source: 'Test',
          },
        ],
      });

      // Step 2: Wait for redirect and extract UMIL ID
      await page.waitForURL(/\/instrument\/(UMIL-\d+)\//);
      const url = page.url();
      const match = url.match(/UMIL-\d+/);
      expect(match).not.toBeNull();

      // Step 3: Delete the instrument
      await instrumentDetailPage.clickDeleteInstrument();
      await instrumentDetailPage.confirmDeleteInstrument();

      // Step 4: Verify redirect to instruments list
      await expect(page).toHaveURL('/instruments/');

      // Step 5: Search for instrument - should not exist
      await instrumentListPage.search(TEST_PATTERNS.deleteName(timestamp));
      const count = await instrumentListPage.getInstrumentCount();
      expect(count).toBe(0);
    },
  );

  authTest(
    'should not show delete button for Wikidata instruments',
    async ({ instrumentDetailPage }) => {
      // Piano is imported from Wikidata in test data
      await instrumentDetailPage.goto(TEST_INSTRUMENT);
      await expect(
        instrumentDetailPage.getDeleteInstrumentButton(),
      ).not.toBeVisible();
    },
  );

  test('should not show delete button when not authenticated', async ({
    instrumentDetailPage,
  }) => {
    await instrumentDetailPage.goto(TEST_INSTRUMENT);

    // Delete button should not be visible without auth
    await expect(instrumentDetailPage.getInstrumentName()).toBeVisible();
    await expect(
      instrumentDetailPage.getDeleteInstrumentButton(),
    ).not.toBeVisible();
  });
});
