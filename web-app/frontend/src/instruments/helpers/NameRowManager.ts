import { WikidataLanguage, NameEntry } from '../Types';

function normalize(str: string): string {
  return str
    .normalize('NFD') // split accents
    .replace(/[\u0300-\u036f]/g, ''); // remove accents
}

export interface NameRowConfig {
  isRequired: boolean;
}

export class NameRowManager {
  private rowIndex: number = 1;
  private languages: WikidataLanguage[];

  constructor(languages: WikidataLanguage[]) {
    this.languages = languages;
  }

  /**
   * Creates a new name row with language, name, and source inputs
   */
  createNameRow(
    index: number,
    config: NameRowConfig = { isRequired: false },
  ): HTMLDivElement {
    const row: HTMLDivElement = document.createElement('div');
    row.classList.add('row', 'mb-2', 'name-row', 'align-items-start');
    row.dataset.rowIndex = String(index);

    const datalistOptions: string = this.languages
      .map((language) => {
        const normalizedAutonym = normalize(language.autonym);
        // Only include normalized version if it's different
        const displayNormalized =
          normalizedAutonym !== language.autonym
            ? ` (${normalizedAutonym})`
            : '';

        return `
        <option
          value="${language.wikidata_code}"
          label="${language.autonym}${displayNormalized} – ${language.en_label}">
        </option>
      `;
      })
      .join('');

    const requiredMark = config.isRequired
      ? '<span class="text-danger">*</span>'
      : '';
    const requiredAttr = config.isRequired ? 'required' : '';
    const deleteButtonStyle = config.isRequired ? 'visibility: hidden;' : '';

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
        this.updateRemoveButtons();
      });
    }

    // Add RTL support for name input based on language selection
    const langInput = row.querySelector(
      `#language${index}`,
    ) as HTMLInputElement;
    const nameInput = row.querySelector(`#name${index}`) as HTMLInputElement;

    langInput.addEventListener('change', () => {
      const lang = this.languages.find(
        (l) => l.wikidata_code === langInput.value,
      );
      if (lang && lang.html_direction) {
        nameInput.setAttribute('dir', lang.html_direction || 'ltr');
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
    rows.forEach((currentRow) => {
      const removeButton = currentRow.querySelector(
        '.remove-row-btn',
      ) as HTMLElement;
      if (!removeButton) return;

      if (rows.length > 1) {
        removeButton.style.visibility = 'visible';
      } else {
        removeButton.style.visibility = 'hidden';
      }
    });
  }

  /**
   * Adds a new name row to the form
   */
  addNameRow(): void {
    this.rowIndex++;
    const nameRows = document.getElementById('nameRows');
    if (nameRows) {
      nameRows.appendChild(this.createNameRow(this.rowIndex));
      this.updateRemoveButtons();
    }
  }

  /**
   * Resets the name rows container and adds one initial row
   */
  resetRows(firstRowRequired: boolean = false): void {
    const nameRows = document.getElementById('nameRows');
    if (nameRows) {
      nameRows.innerHTML = '';
      nameRows.appendChild(
        this.createNameRow(1, { isRequired: firstRowRequired }),
      );
      this.updateRemoveButtons();
      this.rowIndex = 1;
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
   * Collects name entries from all name rows
   */
  collectNameEntries(): NameEntry[] {
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

      const language = languageInput?.value?.trim() || '';
      const name = nameInput?.value?.trim() || '';
      const source = sourceInput?.value?.trim() || '';

      if (language || name || source) {
        entries.push({ language, name, source });
      }
    });

    return entries;
  }

  /**
   * Gets the current row index
   */
  getCurrentRowIndex(): number {
    return this.rowIndex;
  }

  /**
   * Sets the row index (used when restoring form data)
   */
  setRowIndex(index: number): void {
    this.rowIndex = index;
  }
}
