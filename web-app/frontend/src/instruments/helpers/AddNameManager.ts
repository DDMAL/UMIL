import { WikidataLanguage, AddNameForm, NameEntry } from '../Types';
import { NameValidator } from './NameValidator';
import { Modal } from 'bootstrap';

export class AddNameManager {
  private rowIndex: number = 1;
  private languages: WikidataLanguage[];
  private nameValidator: NameValidator;

  constructor(languages: WikidataLanguage[], nameValidator: NameValidator) {
    this.languages = languages;
    this.nameValidator = nameValidator;
  }

  /**
   * Creates a new name row with language, name, and source inputs
   */
  createNameRow(index: number): HTMLDivElement {
    const row: HTMLDivElement = document.createElement('div');
    row.classList.add('row', 'mb-1', 'name-row');

    // Create datalist options dynamically using the languages
    let datalistOptions: string = this.languages
      .map(
        (language: WikidataLanguage) => `
        <option value="${language.wikidata_code}" class="notranslate force-ltr">${language.autonym} - ${language.en_label}</option>
    `,
      )
      .join('');

    row.innerHTML = `
      <div class="col-md-3 language-input">
        <label for="language${index}" class="form-label-sm">Language</label>
        <input list="languages${index}" class="form-control" id="language${index}" name="language[]" placeholder="Type to search" required />
        <datalist id="languages${index}">
          ${datalistOptions}
        </datalist>
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-3 name-input">
        <label for="name${index}" class="form-label-sm">Name</label>
        <input type="text" class="form-control" id="name${index}" name="name[]" placeholder="Enter name" required />
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-3 source-input">
        <label for="source${index}" class="form-label-sm">Source</label>
        <input type="text" class="form-control" id="source${index}" name="source[]" placeholder="Enter source" required />
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-2">
        <label class="form-label-sm">&nbsp;</label>
        <button type="button" class="btn btn-secondary remove-row-btn w-100">Remove</button>
      </div>
    `;

    // Add event listener for remove button
    const removeButton = row.querySelector(
      '.remove-row-btn',
    ) as HTMLButtonElement;
    removeButton.addEventListener('click', () => {
      row.remove();
      this.updateRemoveButtons(); // Ensure correct behavior when rows are removed
    });

    // Add event listener for left/right direction and alignment of the name input based on language selection
    const langInput = row.querySelector(
      `#language${index}`,
    ) as HTMLInputElement;
    const nameInput = row.querySelector(`#name${index}`) as HTMLInputElement;

    langInput.addEventListener('change', () => {
      const lang = this.languages.find(
        (l) => l.wikidata_code === langInput.value,
      );

      if (lang) {
        nameInput.setAttribute('dir', lang.html_direction);
        nameInput.style.textAlign =
          lang.html_direction === 'rtl' ? 'right' : 'left';
      }
    });
    return row;
  }

  /**
   * Updates remove button visibility based on the number of rows
   */
  updateRemoveButtons(): void {
    const rows = document.querySelectorAll('.name-row');
    rows.forEach((currentRow, rowIndex) => {
      const removeButton = currentRow.querySelector('.remove-row-btn');
      // Show the remove button only if there are more than one row
      if (rows.length > 1) {
        (removeButton as HTMLElement).style.display = 'inline-block';
      } else {
        (removeButton as HTMLElement).style.display = 'none'; // Hide the button if only one row remains
      }
    });
  }

  /**
   * Resets the modal and ensures only one row is present
   */
  resetModal(): void {
    const nameRows = document.getElementById('nameRows');
    nameRows.innerHTML = ''; // Clear all rows
    nameRows.appendChild(this.createNameRow(1)); // Add initial row
    this.updateRemoveButtons(); // Ensure remove buttons are updated on reset
    this.rowIndex = 1; // Reset row index
  }

  /**
   * Adds a new name row to the form
   */
  addNameRow(): void {
    this.rowIndex++;
    const nameRows = document.getElementById('nameRows');
    nameRows.appendChild(this.createNameRow(this.rowIndex));
    this.updateRemoveButtons(); // Update remove buttons after adding a new row
  }

  /**
   * Gets the current row index
   */
  getCurrentRowIndex(): number {
    return this.rowIndex;
  }

  /**
   * Sets up event listeners for the add row button
   */
  setupAddRowButton(): void {
    document.getElementById('addRowBtn').addEventListener('click', () => {
      this.addNameRow();
    });
  }

  /**
   * Validates all form rows and shows confirmation modal if valid
   */
  async validateAndSubmitForm(event: Event): Promise<void> {
    event.preventDefault(); // Prevent form submission

    const nameRows = document.querySelectorAll('.name-row');
    let allValid = true;
    let publishResults = ''; // Collect the results for confirmation

    // Validate each row
    for (let row of nameRows) {
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
      const wikidataId = document
        .getElementById('instrumentWikidataIdInModal')
        .textContent.trim();

      // Validate language selection
      const languageResult = this.nameValidator.validateLanguage(languageInput);
      const languageContainer = row.querySelector('.language-input');
      this.nameValidator.displayFeedback(languageContainer, languageResult);

      if (!languageResult.isValid) {
        allValid = false;
        continue;
      }

      try {
        // Comprehensive name validation (uses Wikidata ID for validation if available)
        const validationResult = await this.nameValidator.validateName(
          languageCode,
          nameInput.value,
          sourceInput.value,
          wikidataId,
        );

        // Display feedback for all fields
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

        // Add to confirmation message with better formatting
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
        // Handle validation errors
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

    // If all validation passes, show confirmation modal
    if (allValid) {
      const confirmationModal = new Modal(
        document.getElementById('confirmationModal'),
      );
      document.getElementById('publishResults').innerHTML = publishResults;
      confirmationModal.show();
    }
  }

  /**
   * Sets up form submission handling
   */
  setupFormSubmission(): void {
    document
      .getElementById('addNameForm')
      .addEventListener('submit', (event) => {
        this.validateAndSubmitForm(event);
      });
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
    nameRowsContainer.innerHTML = ''; // Clear existing rows

    if (parsedData['names'] && parsedData['names'].length > 0) {
      parsedData['names'].forEach((rowData: NameEntry, rowIndex: number) => {
        const newRow = this.createNameRow(rowIndex + 1);
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
    this.rowIndex = parsedData['names'] ? parsedData['names'].length : 1;
    this.updateRemoveButtons();
  }
}
