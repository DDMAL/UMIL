import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  async goto() {
    await super.goto('/');
  }

  getVisitEnglishButton(): Locator {
    const isMobile = this.isMobile();
    return this.page.locator(
      isMobile ? 'button.en-site-btn.mobile' : 'button.en-site-btn.desktop',
    );
  }

  getVisitFrenchButton(): Locator {
    const isMobile = this.isMobile();
    return this.page.locator(
      isMobile ? 'button.fr-site-btn.mobile' : 'button.fr-site-btn.desktop',
    );
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
