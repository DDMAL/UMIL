import { AddNameForm, NameEntry } from '../Types';
import { NameValidator } from './NameValidator';
import { NameRowManager } from './NameRowManager';
import { getCsrfToken } from '../../utils/cookies';
import { Modal } from 'bootstrap';

export class AddNameManager {
  private nameRowManager: NameRowManager;
  private nameValidator: NameValidator;

  constructor(nameRowManager: NameRowManager, nameValidator: NameValidator) {
    this.nameRowManager = nameRowManager;
    this.nameValidator = nameValidator;
  }

  /**
   * Sets up the add row button
   */
  setupAddRowButton(): void {
    this.nameRowManager.setupAddRowButton();
  }

  /**
   * Sets up form submission handling
   */
  setupFormSubmission(): void {
    document
      .getElementById('addNameForm')
      ?.addEventListener('submit', (event) => {
        this.validateAndSubmitForm(event);
      });
  }

  /**
   * Sets up the confirm publish button handler
   */
  setupPublishConfirmation(): void {
    document
      .getElementById('confirmPublishBtn')
      ?.addEventListener('click', () => {
        this.submitNames();
      });
  }

  /**
   * Resets the modal to its initial state
   */
  resetModal(): void {
    this.nameRowManager.resetRows();
  }

  /**
   * Validates all form rows and shows confirmation modal if valid
   */
  async validateAndSubmitForm(event: Event): Promise<void> {
    event.preventDefault();

    const nameRows = document.querySelectorAll('.name-row');
    let allValid = true;
    let publishResults = '';

    for (const row of nameRows) {
      const languageInput = row.querySelector(
        'input[list]',
      ) as HTMLInputElement;
      const nameInput = row.querySelector(
        '.name-input input[type="text"]',
      ) as HTMLInputElement;
      const sourceInput = row.querySelector(
        '.source-input input[type="text"]',
      ) as HTMLInputElement;

      const languageCode = languageInput.value;
      const wikidataId =
        document
          .getElementById('instrumentWikidataIdInModal')
          ?.textContent?.trim() || '';

      // Validate language selection
      const languageResult = this.nameValidator.validateLanguage(languageInput);
      const languageContainer = row.querySelector('.language-input');
      this.nameValidator.displayFeedback(languageContainer, languageResult);

      if (!languageResult.isValid) {
        allValid = false;
        continue;
      }

      try {
        const validationResult = await this.nameValidator.validateName(
          languageCode,
          nameInput.value,
          sourceInput.value,
          wikidataId,
        );

        const nameContainer = row.querySelector('.name-input');
        const sourceContainer = row.querySelector('.source-input');

        this.nameValidator.displayFeedback(
          nameContainer,
          validationResult.nameResult,
        );
        this.nameValidator.displayFeedback(
          sourceContainer,
          validationResult.sourceResult,
        );

        if (!validationResult.isValid) {
          allValid = false;
          continue;
        }

        publishResults += `
          <div class="mb-3 p-2 border rounded bg-light">
            <div class="row">
              <div class="col-3"><strong>Language:</strong></div>
              <div class="col-9 notranslate">${languageCode} (${validationResult.languageDescription})</div>
            </div>
            <div class="row">
              <div class="col-3"><strong>Name:</strong></div>
              <div class="col-9">${nameInput.value}</div>
            </div>
            <div class="row">
              <div class="col-3"><strong>Source:</strong></div>
              <div class="col-9">${sourceInput.value}</div>
            </div>
          </div>
        `;
      } catch (error) {
        allValid = false;
        const nameContainer = row.querySelector('.name-input');
        const sourceContainer = row.querySelector('.source-input');

        this.nameValidator.displayFeedback(nameContainer, {
          isValid: false,
          message: 'Error validating name. Please try again.',
          type: 'error',
        });
        this.nameValidator.displayFeedback(sourceContainer, {
          isValid: false,
          message: 'Error validating source. Please try again.',
          type: 'error',
        });
      }
    }

    if (allValid) {
      const confirmationModal = new Modal(
        document.getElementById('confirmationModal'),
      );
      document.getElementById('publishResults').innerHTML = publishResults;
      confirmationModal.show();
    }
  }

  /**
   * Submits name entries to the backend API
   */
  private async submitNames(): Promise<void> {
    const umilId = document
      .getElementById('instrumentUmilIdInModal')
      ?.textContent?.trim();

    const entries = this.nameRowManager.collectNameEntries();

    try {
      const response = await fetch(`/instrument/${umilId}/names/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ entries }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        const addNameModal = Modal.getInstance(
          document.getElementById('addNameModal'),
        );
        const confirmationModal = Modal.getInstance(
          document.getElementById('confirmationModal'),
        );

        addNameModal?.hide();
        confirmationModal?.hide();

        window.location.reload();
      } else {
        alert('Error: ' + data.message);
      }
    } catch (error) {
      alert('An error occurred while publishing: ' + (error as Error).message);
    }
  }

  /**
   * Restores form data from localStorage
   */
  restoreFormData(storedFormData: string): void {
    const addNameForm = document.getElementById(
      'addNameForm',
    ) as HTMLFormElement;
    const parsedData: AddNameForm = JSON.parse(storedFormData);

    // Restore main form values
    for (const fieldKey in parsedData) {
      if ((addNameForm.elements as any)[fieldKey]) {
        (addNameForm.elements as any)[fieldKey].value = (parsedData as any)[
          fieldKey
        ];
      }
    }

    // Restore display_name, umil_id, and wikidata_id
    (
      document.getElementById('instrumentNameInModal') as HTMLElement
    ).textContent = parsedData['display_name'];
    (
      document.getElementById('instrumentUmilIdInModal') as HTMLElement
    ).textContent = parsedData['umil_id'];
    (
      document.getElementById('instrumentWikidataIdInModal') as HTMLElement
    ).textContent = parsedData['wikidata_id'] || '';

    // Restore dynamically added rows
    const nameRowsContainer = document.getElementById(
      'nameRows',
    ) as HTMLElement;
    nameRowsContainer.innerHTML = '';

    if (parsedData['names'] && parsedData['names'].length > 0) {
      parsedData['names'].forEach((rowData: NameEntry, rowIndex: number) => {
        const newRow = this.nameRowManager.createNameRow(rowIndex + 1);
        nameRowsContainer.appendChild(newRow);
        (
          newRow.querySelector('.language-input input') as HTMLInputElement
        ).value = rowData.language;
        (newRow.querySelector('.name-input input') as HTMLInputElement).value =
          rowData.name;
        (
          newRow.querySelector('.source-input input') as HTMLInputElement
        ).value = rowData.source;
      });
    }

    // Update row management state
    this.nameRowManager.setRowIndex(
      parsedData['names'] ? parsedData['names'].length : 1,
    );
    this.nameRowManager.updateRemoveButtons();
  }
}
