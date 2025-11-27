import { test, expect } from '../../fixtures/pages';

test.describe('Mobile Google Translate', () => {
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
    const frSiteCookie = cookies.find((c) => c.name === 'frSite');
    const enSiteCookie = cookies.find((c) => c.name === 'enSite');
    expect(!frSiteCookie || frSiteCookie.value === 'false').toBeTruthy();
    expect(!enSiteCookie || enSiteCookie.value === 'false').toBeTruthy();
    await homePage.toggleMobileNav();
    const aboutLink = page.locator('.nav-link:has-text("About")');
    await expect(aboutLink).toBeVisible();
    await homePage.toggleMobileNav();

    // 2. Click French button, navigate to instruments, check French
    await homePage.getVisitFrenchButton().click();
    await expect(page).toHaveURL(/\/instruments/);
    await homePage.toggleMobileNav();
    const aboutLinkFr = page.locator('.nav-link:has-text("À propos")');
    await expect(aboutLinkFr).toBeVisible();
    await homePage.toggleMobileNav();
    const cookiesAfterFrench = await page.context().cookies();
    const frenchCookie = cookiesAfterFrench.find((c) =>
      c.name.includes('googtrans'),
    );
    expect(frenchCookie?.value).toContain('/en/fr');
    const frSiteCookieAfterFrench = cookiesAfterFrench.find(
      (c) => c.name === 'frSite',
    );
    const enSiteCookieAfterFrench = cookiesAfterFrench.find(
      (c) => c.name === 'enSite',
    );
    expect(frSiteCookieAfterFrench?.value).toBe('true');
    expect(enSiteCookieAfterFrench?.value).toBe('false');

    // 3. Go back to home page, should still be in French
    await homePage.goto();
    await homePage.toggleMobileNav();
    const aboutLinkFrHome = page.locator('.nav-link:has-text("À propos")');
    await expect(aboutLinkFrHome).toBeVisible();
    await homePage.toggleMobileNav();
    const cookiesAfterHome = await page.context().cookies();
    const frSiteCookieAfterHome = cookiesAfterHome.find(
      (c) => c.name === 'frSite',
    );
    const enSiteCookieAfterHome = cookiesAfterHome.find(
      (c) => c.name === 'enSite',
    );
    expect(frSiteCookieAfterHome?.value).toBe('true');
    expect(enSiteCookieAfterHome?.value).toBe('false');

    // 4. Click English button, navigate to instruments, should be in English
    await homePage.getVisitEnglishButton().click();
    await expect(page).toHaveURL(/\/instruments/);

    await page.waitForTimeout(500); // Wait for google translate to update
    await homePage.toggleMobileNav();
    const aboutLinkEn = page.locator('.nav-link:has-text("About")');
    await expect(aboutLinkEn).toBeVisible();
    await homePage.toggleMobileNav();
    const cookiesAfterEnglish = await page.context().cookies();
    const englishCookie = cookiesAfterEnglish.find((c) =>
      c.name.includes('googtrans'),
    );
    expect(!englishCookie || englishCookie.value === '').toBe(true);
    const frSiteCookieAfterEnglish = cookiesAfterEnglish.find(
      (c) => c.name === 'frSite',
    );
    const enSiteCookieAfterEnglish = cookiesAfterEnglish.find(
      (c) => c.name === 'enSite',
    );
    expect(frSiteCookieAfterEnglish?.value).toBe('false');
    expect(enSiteCookieAfterEnglish?.value).toBe('false');
  });
});
