import { test, expect } from '../../fixtures/pages';
import { test as authTest } from '../../fixtures/auth';

test.describe('Desktop Authentication', () => {
  test('should register new user', async ({
    registerPage,
    loginPage,
    page,
  }) => {
    await registerPage.goto();
    const timestamp = Date.now();
    await registerPage.register(
      `testuser${timestamp}@example.com`,
      'TestPassword123!',
      'TestPassword123!',
    );
    await expect(page).toHaveURL(/\/(.*)/);
    await expect(loginPage.getUserDropdown()).toBeVisible();
  });

  test('should login user', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.login('testuser@example.com', 'testpassword');
    await expect(page).toHaveURL('/');
    await expect(loginPage.getUserDropdown()).toBeVisible();
  });

  test('should not show verification and action columns before login', async ({
    instrumentDetailPage,
  }) => {
    await instrumentDetailPage.goto('1');
    await expect(
      instrumentDetailPage.get1stVerificationStatus(),
    ).not.toBeVisible();
    await expect(instrumentDetailPage.get1stActions()).not.toBeVisible();
  });

  authTest(
    'should show verification and action columns after login',
    async ({ instrumentDetailPage }) => {
      await instrumentDetailPage.goto('1');
      await expect(
        instrumentDetailPage.get1stVerificationStatus(),
      ).toBeVisible();
      await expect(instrumentDetailPage.get1stActions()).toBeVisible();
    },
  );
});
