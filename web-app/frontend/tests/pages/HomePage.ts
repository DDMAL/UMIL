import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  async goto() {
    await super.goto('/');
  }

  getEnglishButton(): Locator {
    return this.page
      .locator('button#en-site-btn, a[href*="language=English"] button')
      .first();
  }

  getFrenchButton(): Locator {
    return this.page
      .locator('button#fr-site-btn, a[href*="language=French"] button')
      .first();
  }

  getStatsSection(): Locator {
    return this.page.locator('.stats-section');
  }

  async getStatValue(label: string): Promise<string> {
    const statItem = this.page.locator(`.stat-item:has-text("${label}")`);
    return (await statItem.locator('.stat-number').textContent()) || '';
  }

  async clickInstruments() {
    const link = this.page.locator('.nav-link:has-text("Instruments")');
    await link.click();
  }

  async clickAbout() {
    const link = this.page.locator('.nav-link:has-text("About")');
    await link.click();
  }

  async search(query: string) {
    const searchInput = this.page.locator('input[name="query"]');
    await searchInput.fill(query);
    await searchInput.press('Enter');
  }
}
