import { test, expect } from '../../fixtures/pages';

test.describe('Desktop Google Translate', () => {
  test.use({ blockGoogleTranslate: false });

  test.beforeEach(async ({ homePage }) => {
    await homePage.goto();
  });

  test('should translate site from English to French and back', async ({
    homePage,
    page,
  }) => {
    // 1. Page should start in English
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');

    // 2. Click French button, navigate to instruments, check French
    await homePage.getVisitFrenchButton().click();
    await expect(page).toHaveURL(/\/instruments/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'fr');

    // 3. Go back to home page, should still be in French
    await homePage.goto();
    await expect(page.locator('html')).toHaveAttribute('lang', 'fr');

    // 4. Click English button, navigate to instruments, check English
    await homePage.getVisitEnglishButton().click();
    await expect(page).toHaveURL(/\/instruments/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });
});
