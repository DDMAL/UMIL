import { test as base } from '@playwright/test';
import { readFileSync } from 'fs';
import { join } from 'path';
import {
  HomePage,
  LoginPage,
  RegisterPage,
  InstrumentListPage,
  InstrumentDetailPage,
  CreateInstrumentPage,
} from '../pages';

type PageFixtures = {
  homePage: HomePage;
  loginPage: LoginPage;
  registerPage: RegisterPage;
  instrumentListPage: InstrumentListPage;
  instrumentDetailPage: InstrumentDetailPage;
  createInstrumentPage: CreateInstrumentPage;
};

type TestOptions = {
  /**
   * Controls how Google Translate is handled during E2E tests:
   * - 'block': Completely blocks Google Translate requests (default)
   * - 'stub': Provides a deterministic Google Translate stub for testing
   * - 'allow': Allows real Google Translate to load
   */
  googleTranslateMode: 'block' | 'stub' | 'allow';
};

export const test = base.extend<PageFixtures & TestOptions>({
  googleTranslateMode: ['block', { option: true }],

  page: async ({ page, googleTranslateMode }, use) => {
    if (googleTranslateMode === 'block') {
      // Completely block Google Translate requests
      await page.route('**/translate_a/element.js*', async (route) => {
        await route.abort('blockedbyclient');
      });
    } else if (googleTranslateMode === 'stub') {
      // Load the deterministic stub from external file
      const stubPath = join(__dirname, 'google-translate-stub.js');
      const stubCode = readFileSync(stubPath, 'utf-8');

      await page.route('**/translate_a/element.js*', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/javascript; charset=utf-8',
          body: stubCode,
        });
      });
    }
    // If googleTranslateMode === 'allow', do nothing and let real Google Translate load

    await use(page);
  },

  homePage: async ({ page }, use) => await use(new HomePage(page)),
  loginPage: async ({ page }, use) => await use(new LoginPage(page)),
  registerPage: async ({ page }, use) => await use(new RegisterPage(page)),
  instrumentListPage: async ({ page }, use) =>
    await use(new InstrumentListPage(page)),
  instrumentDetailPage: async ({ page }, use) =>
    await use(new InstrumentDetailPage(page)),
  createInstrumentPage: async ({ page }, use) =>
    await use(new CreateInstrumentPage(page)),
});

export { expect } from '@playwright/test';
