import { test, expect } from '../../fixtures/pages';

test.describe('Mobile Authentication', () => {
  test('should register new user', async ({ registerPage, homePage, page }) => {
    await registerPage.goto();
    const timestamp = Date.now();
    await registerPage.register(
      `testuser${timestamp}@example.com`,
      'TestPassword123!',
      'TestPassword123!',
    );
    await expect(page).toHaveURL(/\/(.*)/);
    await homePage.toggleMobileNav();
    await expect(
      homePage.page.locator('.dropdown:has(svg[aria-label="user icon"])'),
    ).toBeVisible();
  });

  test('should login user', async ({ loginPage, homePage, page }) => {
    await loginPage.goto();
    await loginPage.login('testuser@example.com', 'testpassword');
    await expect(page).toHaveURL('/');
    await homePage.toggleMobileNav();
    await expect(loginPage.getUserDropdown()).toBeVisible();
  });

  test('should not show verification status and actions before login', async ({
    instrumentDetailPage,
  }) => {
    await instrumentDetailPage.goto('1');
    await expect(
      await instrumentDetailPage.get1stVerificationStatus(),
    ).not.toBeVisible();
    await expect(await instrumentDetailPage.get1stActions()).not.toBeVisible();
  });

  test('should show verification status and actions after login', async ({
    loginPage,
    instrumentDetailPage,
  }) => {
    await loginPage.goto();
    await loginPage.login('testuser@example.com', 'testpassword');
    await instrumentDetailPage.goto('1');
    await expect(
      await instrumentDetailPage.get1stVerificationStatus(),
    ).toBeVisible();
    await expect(await instrumentDetailPage.get1stActions()).toBeVisible();
  });
});
