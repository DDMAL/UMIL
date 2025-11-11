import { test as setup } from '@playwright/test';
import { LoginPage } from '../pages';

const authFile = 'tests/.auth/user.json';

setup('authenticate', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('testuser@example.com', 'testpassword');
  await page.waitForURL('/');
  await page.context().storageState({ path: authFile });
});
