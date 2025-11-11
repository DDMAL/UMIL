import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class InstrumentDetailPage extends BasePage {
  async goto(wikidataId: string) {
    await super.goto(`/instrument/${wikidataId}/`);
  }

  getInstrumentName(): Locator {
    return this.page.locator('h2.notranslate').first();
  }

  getWikidataLink(): Locator {
    return this.page.locator('a[href*="wikidata.org"]');
  }

  getHBSClassification(): Locator {
    return this.page.locator(
      'tr:has-text("Hornbostel-Sachs Classification") .view-field',
    );
  }

  getLanguageTable(): Locator {
    return this.page.locator('#languageTableBody');
  }

  getLanguageTableMobile(): Locator {
    return this.page.locator('#languageTableBodyMobile');
  }

  getAddNameButton(): Locator {
    return this.page.locator('button[data-bs-target="#addNameModal"]');
  }

  getToggleLanguagesButton(): Locator {
    return this.page.locator('#toggle-language-table');
  }

  getInstrumentImage(): Locator {
    return this.page.locator('tr:has-text("Image") img');
  }

  async getLanguageNames(): Promise<string[]> {
    const isMobile = this.isMobile();
    const table = isMobile
      ? this.getLanguageTableMobile()
      : this.getLanguageTable();
    const languageCells = isMobile
      ? table.locator('.view-field')
      : table.locator('td:first-child .view-field');
    return await languageCells.allTextContents();
  }

  async deleteNameByLanguage(language: string) {
    const row = this.page.locator(`tr:has-text("${language}")`);
    await row.locator('button:has-text("Delete")').click();
    await this.page
      .locator('#deleteNameModal button:has-text("Delete")')
      .click();
  }

  async addName(language: string, name: string) {
    await this.getAddNameButton().click();
    await this.page
      .locator('#addNameModal select[name="language"]')
      .selectOption(language);
    await this.page.locator('#addNameModal input[name="name"]').fill(name);
    await this.page.locator('#addNameModal button[type="submit"]').click();
  }

  get1stVerificationStatus(): Locator {
    const isMobile = this.isMobile();
    if (isMobile) {
      return this.page
        .locator(
          '#languageTableBodyMobile .fw-bold:has-text("Verification Status")',
        )
        .first();
    }
    return this.page
      .locator('thead th:has-text("Verification Status")')
      .first();
  }

  get1stActions(): Locator {
    const isMobile = this.isMobile();
    const container = isMobile
      ? '#languageTableBodyMobile'
      : '#languageTableBody';
    return this.page.locator(`${container} .action-buttons`).first();
  }
}
