import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class InstrumentDetailPage extends BasePage {
  async goto(umilId: string) {
    await super.goto(`/instrument/${umilId}/`);
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

  // Delete Instrument Methods
  /**
   * Gets the delete instrument button locator.
   * This button only appears for user-created instruments when authenticated.
   */
  getDeleteInstrumentButton(): Locator {
    return this.page.locator('button[data-bs-target="#deleteInstrumentModal"]');
  }

  /**
   * Gets the delete instrument confirmation modal locator.
   */
  getDeleteInstrumentModal(): Locator {
    return this.page.locator('#deleteInstrumentModal');
  }

  /**
   * Gets the confirm delete button inside the modal.
   */
  getConfirmDeleteButton(): Locator {
    return this.page.locator('#confirmDeleteInstrumentBtn');
  }

  /**
   * Gets the error container in the delete modal.
   */
  getDeleteModalError(): Locator {
    return this.page.locator('#deleteModalError');
  }

  /**
   * Gets the error message element in the delete modal.
   */
  getDeleteModalErrorMessage(): Locator {
    return this.page.locator('#deleteModalErrorMessage');
  }

  /**
   * Clicks the delete instrument button and waits for the modal to appear.
   */
  async clickDeleteInstrument(): Promise<void> {
    await this.getDeleteInstrumentButton().click();
    await this.getDeleteInstrumentModal().waitFor({ state: 'visible' });
  }

  /**
   * Confirms the deletion by clicking the confirm button in the modal.
   */
  async confirmDeleteInstrument(): Promise<void> {
    await this.getConfirmDeleteButton().click();
  }

  // Name Verification Methods
  /**
   * Checks if a name exists for a given language.
   * @param language - The language display name (e.g., "English", "French")
   * @param name - The instrument name to look for
   * @returns true if the name is visible in the table
   */
  async hasName(language: string, name: string): Promise<boolean> {
    const row = this.page.locator(
      `tr:has-text("${language}"):has-text("${name}")`,
    );
    return await row.isVisible();
  }

  /**
   * Gets the total count of instrument names displayed.
   * Handles both desktop and mobile views.
   * @returns The number of name entries displayed
   */
  async getNameCount(): Promise<number> {
    const isMobile = this.isMobile();
    if (isMobile) {
      // Mobile view: count name cards/rows
      return await this.page
        .locator('#languageTableBodyMobile .name-card')
        .count();
    }
    // Desktop view: count table rows
    return await this.page.locator('#languageTableBody tr').count();
  }

  /**
   * Checks if the delete instrument button is visible.
   * Delete button only appears for user-created instruments when authenticated.
   * @returns true if delete button is visible
   */
  async isDeleteButtonVisible(): Promise<boolean> {
    return await this.getDeleteInstrumentButton().isVisible();
  }
}
