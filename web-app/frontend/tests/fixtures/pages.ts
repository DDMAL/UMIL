import { test as base } from '@playwright/test';
import {
  HomePage,
  LoginPage,
  RegisterPage,
  InstrumentListPage,
  InstrumentDetailPage,
} from '../pages';

type PageFixtures = {
  homePage: HomePage;
  loginPage: LoginPage;
  registerPage: RegisterPage;
  instrumentListPage: InstrumentListPage;
  instrumentDetailPage: InstrumentDetailPage;
};

type TestOptions = {
  /**
   * When enabled, aborts the external Google Translate script request to avoid
   * rate limiting (HTTP 429) during E2E runs.
   */
  blockGoogleTranslate: boolean;
};

export const test = base.extend<PageFixtures & TestOptions>({
  blockGoogleTranslate: [true, { option: true }],

  page: async ({ page, blockGoogleTranslate }, use) => {
    if (blockGoogleTranslate) {
      // Keep the <script> tag happy without hitting Google's servers.
      await page.route('**/translate_a/element.js*', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/javascript; charset=utf-8',
          body: '',
        });
      });
    }

    await use(page);
  },

  homePage: async ({ page }, use) => await use(new HomePage(page)),
  loginPage: async ({ page }, use) => await use(new LoginPage(page)),
  registerPage: async ({ page }, use) => await use(new RegisterPage(page)),
  instrumentListPage: async ({ page }, use) =>
    await use(new InstrumentListPage(page)),
  instrumentDetailPage: async ({ page }, use) =>
    await use(new InstrumentDetailPage(page)),
});

export { expect } from '@playwright/test';
