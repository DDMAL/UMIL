import { test as base } from '@playwright/test';
import {
  HomePage,
  LoginPage,
  InstrumentListPage,
  InstrumentDetailPage,
} from '../pages';

const authFile = 'tests/.auth/user.json';

type PageFixtures = {
  homePage: HomePage;
  loginPage: LoginPage;
  instrumentListPage: InstrumentListPage;
  instrumentDetailPage: InstrumentDetailPage;
};

export const test = base.extend<PageFixtures>({
  storageState: authFile,
  homePage: async ({ page }, use) => await use(new HomePage(page)),
  loginPage: async ({ page }, use) => await use(new LoginPage(page)),
  instrumentListPage: async ({ page }, use) =>
    await use(new InstrumentListPage(page)),
  instrumentDetailPage: async ({ page }, use) =>
    await use(new InstrumentDetailPage(page)),
});

export { expect } from '@playwright/test';
