import {
  WikidataLanguage,
  NameEntry,
  CreateInstrumentResponse,
  ValidationResult,
} from '../Types';
import {
  CreateInstrumentValidator,
  CreateInstrumentData,
} from './CreateInstrumentValidator';
import { getCsrfToken } from '../../utils/cookies';
import { Modal } from 'bootstrap';

export class CreateInstrumentManager {
  private rowIndex: number = 1;
  private languages: WikidataLanguage[];
  private validator: CreateInstrumentValidator;

  constructor(
    languages: WikidataLanguage[],
    validator: CreateInstrumentValidator,
  ) {
    this.languages = languages;
    this.validator = validator;
  }

  /**
   * Creates a new name row with language, name, and source inputs
   */
  createNameRow(index: number, isFirst: boolean = false): HTMLDivElement {
    const row: HTMLDivElement = document.createElement('div');
    row.classList.add('row', 'mb-2', 'name-row', 'align-items-start');
    row.dataset.rowIndex = String(index);

    const datalistOptions: string = this.languages
      .map(
        (language: WikidataLanguage) => `
        <option value="${language.wikidata_code}" class="notranslate force-ltr">
          ${language.autonym} - ${language.en_label}
        </option>
      `,
      )
      .join('');

    const requiredMark = isFirst ? '<span class="text-danger">*</span>' : '';
    const requiredAttr = isFirst ? 'required' : '';
    const deleteButtonStyle = isFirst ? 'visibility: hidden;' : '';

    row.innerHTML = `
      <div class="col-md-3 col-12 language-input mb-2 mb-md-0">
        <label for="language${index}" class="form-label">Language ${requiredMark}</label>
        <input list="languages${index}" class="form-control" id="language${index}"
               name="language[]" placeholder="Type to search" ${requiredAttr} />
        <datalist id="languages${index}">
          ${datalistOptions}
        </datalist>
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-3 col-12 name-input mb-2 mb-md-0">
        <label for="name${index}" class="form-label">Name ${requiredMark}</label>
        <input type="text" class="form-control" id="name${index}"
               name="name[]" placeholder="Enter name" ${requiredAttr} />
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-3 col-12 source-input mb-2 mb-md-0">
        <label for="source${index}" class="form-label">Source ${requiredMark}</label>
        <input type="text" class="form-control" id="source${index}"
               name="source[]" placeholder="Enter source" ${requiredAttr} />
        <div class="valid-feedback"></div>
        <div class="invalid-feedback"></div>
      </div>
      <div class="col-md-2 col-12 mb-2 mb-md-0 align-self-end d-flex justify-content-center">
        <button type="button" class="btn btn-outline-danger remove-row-btn w-50" title="Remove this row" style="${deleteButtonStyle}">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    `;

    // Add event listener for remove button
    const removeButton = row.querySelector(
      '.remove-row-btn',
    ) as HTMLButtonElement;
    if (removeButton) {
      removeButton.addEventListener('click', () => {
        row.remove();
      });
    }

    // Add RTL support for name input based on language
    const langInput = row.querySelector(
      `#language${index}`,
    ) as HTMLInputElement;
    const nameInput = row.querySelector(`#name${index}`) as HTMLInputElement;

    langInput.addEventListener('change', () => {
      const lang = this.languages.find(
        (l) => l.wikidata_code === langInput.value,
      );
      if (lang) {
        nameInput.setAttribute('dir', lang.html_direction || 'ltr');
        nameInput.style.textAlign =
          lang.html_direction === 'rtl' ? 'right' : 'left';
      }
    });

    return row;
  }

  /**
   * Initializes the form with one required row
   */
  initializeForm(): void {
    const nameRows = document.getElementById('nameRows');
    if (nameRows) {
      nameRows.innerHTML = '';
      nameRows.appendChild(this.createNameRow(1, true));
      this.rowIndex = 1;
    }
  }

  /**
   * Adds a new optional name row
   */
  addNameRow(): void {
    this.rowIndex++;
    const nameRows = document.getElementById('nameRows');
    if (nameRows) {
      nameRows.appendChild(this.createNameRow(this.rowIndex, false));
    }
  }

  /**
   * Sets up the add row button
   */
  setupAddRowButton(): void {
    const addRowBtn = document.getElementById('addRowBtn');
    if (addRowBtn) {
      addRowBtn.addEventListener('click', () => this.addNameRow());
    }
  }

  /**
   * Sets up HBS classification validation on blur
   */
  setupHbsValidation(): void {
    const hbsInput = document.getElementById(
      'hornbostelSachsClass',
    ) as HTMLInputElement;
    if (hbsInput) {
      hbsInput.addEventListener('blur', () => {
        const result = this.validator.validateHbsClassification(hbsInput.value);
        const container = hbsInput.parentElement!;
        this.validator.displayFeedback(container, result);
      });
    }
  }

  /**
   * Toggles image source field visibility based on image selection
   */
  setupImageFieldToggle(): void {
    const imageInput = document.getElementById('image') as HTMLInputElement;
    const imageSourceContainer = document.getElementById(
      'imageSourceContainer',
    );
    const imagePreview = document.getElementById(
      'imagePreview',
    ) as HTMLImageElement;
    const imagePreviewContainer = document.getElementById(
      'imagePreviewContainer',
    );

    if (imageInput && imageSourceContainer) {
      imageInput.addEventListener('change', () => {
        const files = imageInput.files;
        if (files && files.length > 0) {
          imageSourceContainer.classList.remove('d-none');
          const sourceInput = imageSourceContainer.querySelector(
            'input',
          ) as HTMLInputElement;
          if (sourceInput) {
            sourceInput.required = true;
          }

          // Show image preview
          if (imagePreview && imagePreviewContainer) {
            const reader = new FileReader();
            reader.onload = (e) => {
              imagePreview.src = e.target?.result as string;
              imagePreviewContainer.classList.remove('d-none');
            };
            reader.readAsDataURL(files[0]);
          }
        } else {
          imageSourceContainer.classList.add('d-none');
          const sourceInput = imageSourceContainer.querySelector(
            'input',
          ) as HTMLInputElement;
          if (sourceInput) {
            sourceInput.required = false;
            sourceInput.value = '';
          }

          // Hide image preview
          if (imagePreviewContainer) {
            imagePreviewContainer.classList.add('d-none');
          }
        }
      });
    }
  }

  /**
   * Collects form data
   */
  collectFormData(): CreateInstrumentData {
    const entries: NameEntry[] = [];
    const nameRows = document.querySelectorAll('.name-row');

    nameRows.forEach((row) => {
      const languageInput = row.querySelector(
        'input[list]',
      ) as HTMLInputElement;
      const nameInput = row.querySelector(
        '.name-input input[type="text"]',
      ) as HTMLInputElement;
      const sourceInput = row.querySelector(
        '.source-input input[type="text"]',
      ) as HTMLInputElement;

      // Include entry if any field has data
      const language = languageInput?.value?.trim() || '';
      const name = nameInput?.value?.trim() || '';
      const source = sourceInput?.value?.trim() || '';

      if (language || name || source) {
        entries.push({ language, name, source });
      }
    });

    const instrumentSource =
      (
        document.getElementById('instrumentSource') as HTMLInputElement
      )?.value?.trim() || '';
    const hbsClass =
      (
        document.getElementById('hornbostelSachsClass') as HTMLInputElement
      )?.value?.trim() || '';

    const imageInput = document.getElementById('image') as HTMLInputElement;
    const imageFile =
      imageInput?.files && imageInput.files.length > 0
        ? imageInput.files[0]
        : null;

    const imageSource =
      (
        document.getElementById('imageSource') as HTMLInputElement
      )?.value?.trim() || '';

    return {
      entries,
      instrument_source: instrumentSource,
      hornbostel_sachs_class: hbsClass,
      image_file: imageFile,
      image_source: imageSource,
    };
  }

  /**
   * Validates and submits the form
   */
  async validateAndSubmitForm(event: Event): Promise<void> {
    event.preventDefault();

    // Clear previous validation states
    document.querySelectorAll('.is-valid, .is-invalid').forEach((el) => {
      el.classList.remove('is-valid', 'is-invalid');
    });

    // Clear nameRows error
    const nameRowsError = document.getElementById('nameRowsError');
    if (nameRowsError) {
      nameRowsError.style.display = 'none';
      nameRowsError.textContent = '';
    }

    const formData = this.collectFormData();
    const validationResult = await this.validator.validateAll(formData);

    if (!validationResult.isValid) {
      // Display validation errors
      this.displayValidationErrors(validationResult.errors);
      return;
    }

    // Show confirmation modal
    this.showConfirmationModal(formData);
  }

  /**
   * Displays validation errors on the form
   */
  displayValidationErrors(errors: Map<string, ValidationResult>): void {
    errors.forEach((result, fieldId) => {
      let container: Element | null = null;

      // Special handling for nameRows error
      if (fieldId === 'nameRows') {
        const errorDiv = document.getElementById('nameRowsError');
        if (errorDiv) {
          errorDiv.textContent = result.message;
          errorDiv.style.display = 'block';
        }
        return; // Skip standard processing
      }

      // Handle different field types
      if (fieldId.startsWith('language')) {
        const rowIndex = fieldId.replace('language', '');
        const row = document.querySelector(
          `.name-row[data-row-index="${rowIndex}"]`,
        );
        if (row) {
          container = row.querySelector('.language-input');
        }
      } else if (fieldId.startsWith('name')) {
        const rowIndex = fieldId.replace('name', '');
        const row = document.querySelector(
          `.name-row[data-row-index="${rowIndex}"]`,
        );
        if (row) {
          container = row.querySelector('.name-input');
        }
      } else if (
        fieldId.startsWith('source') &&
        !fieldId.includes('instrument')
      ) {
        const rowIndex = fieldId.replace('source', '');
        const row = document.querySelector(
          `.name-row[data-row-index="${rowIndex}"]`,
        );
        if (row) {
          container = row.querySelector('.source-input');
        }
      } else {
        const field = document.getElementById(fieldId);
        if (field) {
          container = field.parentElement;
        }
      }

      if (container) {
        this.validator.displayFeedback(container, result);
      }
    });

    // Scroll to first error
    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      // If no field-level error, check for nameRows error
      const nameRowsError = document.getElementById('nameRowsError');
      if (nameRowsError && nameRowsError.style.display !== 'none') {
        nameRowsError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }

  /**
   * Shows confirmation modal before submission
   */
  showConfirmationModal(formData: CreateInstrumentData): void {
    // Clear any previous errors from the modal
    this.hideModalError();

    // Filter out empty entries
    const validEntries = formData.entries.filter(
      (e) => e.language && e.name && e.source,
    );

    const publishResults = document.getElementById('publishResults');
    if (!publishResults) return;
    publishResults.textContent = '';

    this.appendLabeledRow(
      publishResults,
      'Instrument Source:',
      formData.instrument_source,
    );
    this.appendLabeledRow(
      publishResults,
      'HBS Classification:',
      formData.hornbostel_sachs_class,
    );

    const namesDiv = document.createElement('div');
    namesDiv.classList.add('mb-3');
    const namesLabel = document.createElement('strong');
    namesLabel.textContent = 'Names:';
    namesDiv.appendChild(namesLabel);

    const ul = document.createElement('ul');
    ul.classList.add('list-unstyled', 'ms-3', 'mt-2');
    for (const e of validEntries) {
      const li = document.createElement('li');
      li.classList.add('mb-2');

      const badge = document.createElement('span');
      badge.classList.add('badge', 'bg-primary', 'me-2');
      badge.textContent = e.language;

      const nameEl = document.createElement('strong');
      nameEl.textContent = e.name;

      const sourceEl = document.createElement('small');
      sourceEl.classList.add('text-muted');
      sourceEl.textContent = 'Source: ' + e.source;

      li.appendChild(badge);
      li.appendChild(nameEl);
      li.appendChild(document.createElement('br'));
      li.appendChild(sourceEl);
      ul.appendChild(li);
    }
    namesDiv.appendChild(ul);
    publishResults.appendChild(namesDiv);

    if (formData.image_file) {
      const imageDiv = document.createElement('div');
      imageDiv.classList.add('mb-2');

      const imageLabel = document.createElement('strong');
      imageLabel.textContent = 'Image: ';
      imageDiv.appendChild(imageLabel);
      imageDiv.appendChild(document.createTextNode(formData.image_file.name));
      imageDiv.appendChild(document.createElement('br'));

      const imageSource = document.createElement('small');
      imageSource.classList.add('text-muted');
      imageSource.textContent = 'Source: ' + (formData.image_source || '');
      imageDiv.appendChild(imageSource);

      publishResults.appendChild(imageDiv);
    }

    const modal = new Modal(document.getElementById('confirmationModal')!);
    modal.show();
  }

  private appendLabeledRow(
    parent: HTMLElement,
    label: string,
    value: string,
  ): void {
    const div = document.createElement('div');
    div.classList.add('mb-2');
    const strong = document.createElement('strong');
    strong.textContent = label;
    div.appendChild(strong);
    div.appendChild(document.createTextNode(' ' + value));
    parent.appendChild(div);
  }

  /**
   * Submits the instrument to the API
   */
  async submitInstrument(): Promise<void> {
    const formData = this.collectFormData();

    // Filter out empty entries
    const validEntries = formData.entries.filter(
      (e) => e.language && e.name && e.source,
    );

    // Create FormData for multipart upload
    const submitData = new FormData();
    submitData.append('entries', JSON.stringify(validEntries));
    submitData.append('instrument_source', formData.instrument_source);
    submitData.append(
      'hornbostel_sachs_class',
      formData.hornbostel_sachs_class,
    );

    if (formData.image_file) {
      submitData.append('image', formData.image_file);
      submitData.append('image_source', formData.image_source || '');
    }

    // Show loading state
    const confirmBtn = document.getElementById(
      'confirmCreateBtn',
    ) as HTMLButtonElement;
    const originalText = confirmBtn.innerHTML;
    confirmBtn.disabled = true;
    confirmBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status"></span> Creating...';

    try {
      const response = await fetch('/api/instrument/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
        body: submitData,
      });

      const data: CreateInstrumentResponse = await response.json();

      // Check HTTP status first
      if (!response.ok) {
        // HTTP error (4xx, 5xx) - includes rate limiting (429)
        const errorMessage =
          data.message ||
          `Server error: ${response.status} ${response.statusText}`;
        this.showModalError(errorMessage);
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
        return;
      }

      // Check application-level success
      if (data.status === 'success' && data.umil_id) {
        // Redirect to the new instrument's detail page
        window.location.href = `/instrument/${data.umil_id}/`;
      } else {
        // Application error with 200 status
        this.showModalError('Error: ' + data.message);
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
      }
    } catch (error) {
      // Network error or JSON parsing error
      this.showModalError(
        'An error occurred while creating the instrument: ' +
          (error as Error).message,
      );
      confirmBtn.disabled = false;
      confirmBtn.innerHTML = originalText;
    }
  }

  /**
   * Displays error message in the confirmation modal
   */
  private showModalError(message: string): void {
    const modalError = document.getElementById('modalError');
    const modalErrorMessage = document.getElementById('modalErrorMessage');

    if (modalError && modalErrorMessage) {
      modalErrorMessage.textContent = message;
      modalError.style.display = 'block';
      modalError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  /**
   * Hides error message in the confirmation modal
   */
  private hideModalError(): void {
    const modalError = document.getElementById('modalError');
    if (modalError) {
      modalError.style.display = 'none';
    }
  }

  /**
   * Sets up form submission handling
   */
  setupFormSubmission(): void {
    const form = document.getElementById('createInstrumentForm');
    if (form) {
      form.addEventListener('submit', (event) =>
        this.validateAndSubmitForm(event),
      );
    }

    // Confirm button handler
    const confirmBtn = document.getElementById('confirmCreateBtn');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => {
        this.submitInstrument();
      });
    }
  }
}
