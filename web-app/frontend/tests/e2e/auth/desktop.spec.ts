import { test, expect } from '../../fixtures/pages';
import { test as authTest } from '../../fixtures/auth';
import { extractVerificationUrl } from '../../helpers/email';

test.describe('Desktop Authentication', () => {
  test('should register new user', async ({
    registerPage,
    loginPage,
    page,
  }) => {
    await registerPage.goto();
    const timestamp = Date.now();
    const email = `testuser${timestamp}@example.com`;
    const password = 'TestPassword123!';

    // Register new user
    await registerPage.register(email, password, password);

    // Should redirect to login page with success message
    await expect(page).toHaveURL('/accounts/login/');
    await expect(
      page.locator('text=/Please check your email to verify/i'),
    ).toBeVisible();

    // Extract verification URL from Docker logs
    const verificationUrl = await extractVerificationUrl(email);

    // Navigate to verification URL
    await page.goto(verificationUrl);

    // Should see verification success message
    await expect(
      page.locator('text=/Email verified successfully/i'),
    ).toBeVisible();

    // Login with verified account
    await loginPage.login(email, password);
    await expect(page).toHaveURL('/');
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
