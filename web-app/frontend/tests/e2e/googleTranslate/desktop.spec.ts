import { test, expect } from '../../fixtures/pages';

test.describe('Desktop Google Translate', () => {
  test.beforeEach(async ({ homePage }) => {
    await homePage.goto();
  });

  test('should translate site from English to French and back', async ({
    homePage,
    page,
  }) => {
    // 1. Page should start in English
    const cookies = await page.context().cookies();
    const googleTranslateCookie = cookies.find((c) =>
      c.name.includes('googtrans'),
    );
    expect(
      !googleTranslateCookie || googleTranslateCookie.value === '/en/en',
    ).toBeTruthy();
    const aboutLink = page.locator('.nav-link:has-text("About")');
    await expect(aboutLink).toBeVisible();

    // 2. Click French button, navigate to instruments, check French
    await homePage.getVisitFrenchButton().click();
    await expect(page).toHaveURL(/\/instruments/);
    const aboutLinkFr = page.locator('.nav-link:has-text("À propos")');
    await expect(aboutLinkFr).toBeVisible();
    const cookiesAfterFrench = await page.context().cookies();
    const frenchCookie = cookiesAfterFrench.find((c) =>
      c.name.includes('googtrans'),
    );
    expect(frenchCookie?.value).toContain('/en/fr');

    // 3. Go back to home page, should still be in French
    await homePage.goto();
    const aboutLinkFrHome = page.locator('.nav-link:has-text("À propos")');
    await expect(aboutLinkFrHome).toBeVisible();

    // 4. Click English button, navigate to instruments, check English
    await homePage.getVisitEnglishButton().click();
    await expect(page).toHaveURL(/\/instruments/);
    const aboutLinkEn = page.locator('.nav-link:has-text("About")');
    await expect(aboutLinkEn).toBeVisible();
    await page.waitForTimeout(500);
    const cookiesAfterEnglish = await page.context().cookies();
    const englishCookie = cookiesAfterEnglish.find((c) =>
      c.name.includes('googtrans'),
    );
    expect(!englishCookie || englishCookie.value === '').toBe(true);
  });
});
