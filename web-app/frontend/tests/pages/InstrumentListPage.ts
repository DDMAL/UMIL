import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class InstrumentListPage extends BasePage {
  async goto() {
    await super.goto('/instruments/');
  }

  getSearchInput(): Locator {
    return this.page.locator('input[name="query"]');
  }

  getInstrumentCards(): Locator {
    return this.page.locator('.instrument-card, .card');
  }

  getHBSFilter(value: string): Locator {
    return this.page.locator(`li[current-value="${value}"]`);
  }

  getClearAllFiltersButton(): Locator {
    return this.page.locator('a:has-text("Clear All")');
  }

  getLanguageDropdown(): Locator {
    return this.page.locator('#language-dropdown-btn');
  }

  getMasonryViewButton(): Locator {
    return this.page.locator('#masonry-btn');
  }

  getStandardViewButton(): Locator {
    return this.page.locator('#std-btn');
  }

  getPaginationInfo(): Locator {
    return this.page.locator('#instrumentNum');
  }

  async search(query: string) {
    await this.getSearchInput().fill(query);
    await this.getSearchInput().press('Enter');
  }

  async clickInstrument(name: string) {
    const card = this.page
      .locator(
        `.instrument-card:has-text("${name}"), .card:has-text("${name}")`,
      )
      .first();
    await card.click();
  }

  async getInstrumentCount(): Promise<number> {
    await this.page.waitForSelector('.instrument-card, .card', {
      timeout: 5000,
    });
    return await this.getInstrumentCards().count();
  }

  async selectLanguage(language: string) {
    await this.getLanguageDropdown().click();
    await this.page.locator(`a[data-language="${language}"]`).click();
  }

  async filterByHBS(value: string) {
    await this.getHBSFilter(value).click();
  }
}
