import { Page, Locator } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  readonly baseURL: string;

  constructor(page: Page) {
    this.page = page;
    this.baseURL = page.context().browser()?.browserType().name()
      ? 'http://localhost:8000'
      : '';
  }

  async goto(path: string) {
    await this.page.goto(path);
  }

  async waitForURL(path: string) {
    await this.page.waitForURL(path);
  }

  async isMobile(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width < 768 : false;
  }

  getNavbar(): Locator {
    return this.page.locator('.navbar');
  }

  getHamburgerButton(): Locator {
    return this.page.locator('.navbar-toggler');
  }

  getNavbarMenu(): Locator {
    return this.page.locator('#navbarMenu');
  }

  async isNavbarExpanded(): Promise<boolean> {
    const navbarMenu = this.getNavbarMenu();
    const classes = await navbarMenu.getAttribute('class');
    return classes?.includes('show') || false;
  }

  async toggleMobileNav() {
    if (await this.isMobile()) {
      await this.getHamburgerButton().click();
      await this.page.waitForTimeout(300); // Wait for animation
    }
  }
}
