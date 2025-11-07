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

export const test = base.extend<PageFixtures>({
  homePage: async ({ page }, use) => await use(new HomePage(page)),
  loginPage: async ({ page }, use) => await use(new LoginPage(page)),
  registerPage: async ({ page }, use) => await use(new RegisterPage(page)),
  instrumentListPage: async ({ page }, use) =>
    await use(new InstrumentListPage(page)),
  instrumentDetailPage: async ({ page }, use) =>
    await use(new InstrumentDetailPage(page)),
});

export { expect } from '@playwright/test';
