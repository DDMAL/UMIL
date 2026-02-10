import { Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export interface InstrumentData {
  instrumentSource: string;
  hbsClass: string;
  names: Array<{
    language: string;
    name: string;
    source: string;
  }>;
  image?: string;
  imageSource?: string;
}

export class CreateInstrumentPage extends BasePage {
  async goto() {
    await super.goto('/instrument/create/');
  }

  getInstrumentSourceInput(): Locator {
    return this.page.locator('#instrumentSource');
  }

  getHBSClassInput(): Locator {
    return this.page.locator('#hornbostelSachsClass');
  }

  getImageInput(): Locator {
    return this.page.locator('#image');
  }

  getImageSourceInput(): Locator {
    return this.page.locator('#imageSource');
  }

  getImageSourceContainer(): Locator {
    return this.page.locator('#imageSourceContainer');
  }

  getImagePreviewContainer(): Locator {
    return this.page.locator('#imagePreviewContainer');
  }

  getImagePreview(): Locator {
    return this.page.locator('#imagePreview');
  }

  getSubmitButton(): Locator {
    return this.page.locator('#createInstrumentForm button[type="submit"]');
  }

  getAddRowButton(): Locator {
    return this.page.locator('#addRowBtn');
  }

  getConfirmationModal(): Locator {
    return this.page.locator('#confirmationModal');
  }

  getConfirmButton(): Locator {
    return this.page.locator('#confirmCreateBtn');
  }

  getModalError(): Locator {
    return this.page.locator('#modalError');
  }

  getModalErrorMessage(): Locator {
    return this.page.locator('#modalErrorMessage');
  }

  getNameRows(): Locator {
    return this.page.locator('#nameRows .name-row');
  }

  async getNameRowCount(): Promise<number> {
    return await this.getNameRows().count();
  }

  /**
   * Fills a name row with language, name, and source data.
   * @param index - Zero-based index of the row to fill
   * @param nameData - Object containing language, name, and source
   */
  async fillNameRow(
    index: number,
    nameData: InstrumentData['names'][0],
  ): Promise<void> {
    const row = this.getNameRows().nth(index);
    await row.locator('input[list="languages-list"]').fill(nameData.language);
    await row.locator('input[name="name"]').fill(nameData.name);
    await row.locator('input[name="source"]').fill(nameData.source);
  }

  /**
   * Removes a name row at the specified index.
   * @param index - Zero-based index of the row to remove
   */
  async removeNameRow(index: number): Promise<void> {
    const row = this.getNameRows().nth(index);
    await row.locator('button.remove-row-btn').click();
  }

  /**
   * Waits for the confirmation modal to become visible.
   */
  async waitForConfirmationModal(): Promise<void> {
    await this.getConfirmationModal().waitFor({ state: 'visible' });
  }

  /**
   * Creates an instrument with the provided data.
   * Fills the form, submits it, and confirms creation through the modal.
   * @param data - Instrument metadata, names, and optional image
   */
  async createInstrument(data: InstrumentData): Promise<void> {
    // Fill instrument metadata
    await this.getInstrumentSourceInput().fill(data.instrumentSource);
    await this.getHBSClassInput().fill(data.hbsClass);

    // Fill name rows
    for (let i = 0; i < data.names.length; i++) {
      const nameData = data.names[i];

      // Add additional row if needed (first row exists by default)
      if (i > 0) {
        await this.getAddRowButton().click();
        // Wait for the new row to appear
        await expect(this.getNameRows()).toHaveCount(i + 1);
      }

      await this.fillNameRow(i, nameData);
    }

    // Upload image if provided
    if (data.image) {
      await this.getImageInput().setInputFiles(data.image);
      if (data.imageSource) {
        await this.getImageSourceInput().fill(data.imageSource);
      }
    }

    // Submit form
    await this.getSubmitButton().click();

    // Wait for confirmation modal
    await this.waitForConfirmationModal();

    // Confirm creation
    await this.getConfirmButton().click();
  }

  async hasValidationError(fieldId: string): Promise<boolean> {
    const field = this.page.locator(`#${fieldId}`);
    const classList = await field.getAttribute('class');
    return classList?.includes('is-invalid') || false;
  }

  /**
   * Gets the validation error message for a field.
   * Tries multiple selector strategies to handle different form layouts.
   * @param fieldId - The ID of the field to check
   * @returns The error message text, or null if no error is visible
   */
  async getValidationError(fieldId: string): Promise<string | null> {
    // Try multiple selectors to handle different form layouts
    const feedbackSelectors = [
      `#${fieldId} ~ .invalid-feedback`, // Sibling
      `#${fieldId}-feedback`, // By ID convention
      `.${fieldId}-feedback`, // By class
    ];

    for (const selector of feedbackSelectors) {
      const feedback = this.page.locator(selector);
      if (await feedback.isVisible()) {
        return await feedback.textContent();
      }
    }

    return null;
  }
}
