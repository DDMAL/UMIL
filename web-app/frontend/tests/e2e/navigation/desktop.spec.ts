import { test, expect } from '../../fixtures/pages';

test.describe('Desktop Navigation', () => {
  test.beforeEach(async ({ homePage }) => {
    await homePage.goto();
  });

  test('should navigate to UMIL home page', async ({ homePage, page }) => {
    await homePage.goto();
    const homeLink = page.locator('.nav-link:has-text("UMIL")');
    await homeLink.click();
    await expect(page).toHaveURL('/');
  });

  test('should navigate to Instruments page', async ({ page }) => {
    const instrumentsLink = page.locator('.nav-link:has-text("Instruments")');
    await instrumentsLink.click();
    await expect(page).toHaveURL(/\/instruments/);
  });

  test('should navigate to About page', async ({ page }) => {
    const aboutLink = page.locator('.nav-link:has-text("About")');
    await aboutLink.click();
    await expect(page).toHaveURL(/\/about/);
  });

  test('should perform search from navigation bar', async ({ page }) => {
    const searchInput = page.locator('.search-input');
    await searchInput.fill('guitar');
    await searchInput.press('Enter');
    await expect(page).toHaveURL(/query=guitar/);
  });

  test('should display login button and navigate to login page', async ({
    page,
  }) => {
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible();
    await loginButton.click();
    await expect(page).toHaveURL(/\/login/);
  });
});
