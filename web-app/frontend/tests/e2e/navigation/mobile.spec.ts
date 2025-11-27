import { test, expect } from '../../fixtures/pages';

test.describe('Mobile Navigation', () => {
  test.beforeEach(async ({ homePage }) => {
    await homePage.goto();
  });

  test('should toggle hamburger menu', async ({ homePage }) => {
    const hamburgerButton = homePage.getHamburgerButton();
    await expect(hamburgerButton).toBeVisible();

    await hamburgerButton.click();
    await homePage.page.waitForTimeout(500); // Wait for animation
    expect(await homePage.isNavbarExpanded()).toBe(true);

    await hamburgerButton.click();
    await homePage.page.waitForTimeout(500); // Wait for animation
    expect(await homePage.isNavbarExpanded()).toBe(false);
  });

  test('should navigate to UMIL home page from mobile menu', async ({
    homePage,
    page,
  }) => {
    await homePage.toggleMobileNav();
    const homeLink = page.locator('.nav-link:has-text("UMIL")');
    await homeLink.click();
    await expect(page).toHaveURL('/');
  });

  test('should navigate to Instruments page from mobile menu', async ({
    homePage,
    page,
  }) => {
    await homePage.toggleMobileNav();
    const instrumentsLink = page.locator('.nav-link:has-text("Instruments")');
    await instrumentsLink.click();
    await expect(page).toHaveURL(/\/instruments/);
  });

  test('should navigate to About page from mobile menu', async ({
    homePage,
    page,
  }) => {
    await homePage.toggleMobileNav();
    const aboutLink = page.locator('.nav-link:has-text("About")');
    await aboutLink.click();
    await expect(page).toHaveURL(/\/about/);
  });

  test('should perform search from navigation bar', async ({
    homePage,
    page,
  }) => {
    await homePage.toggleMobileNav();
    const searchInput = page.locator('.search-input');
    await searchInput.fill('guitar');
    await searchInput.press('Enter');
    await expect(page).toHaveURL(/query=guitar/);
  });

  test('should display login button and navigate to login page', async ({
    homePage,
    page,
  }) => {
    await homePage.toggleMobileNav();
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible();
    await loginButton.click();
    await expect(page).toHaveURL(/\/login/);
  });
});
