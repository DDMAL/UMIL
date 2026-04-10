import { WikidataLanguage, ValidationResult, NameEntry } from '../Types';
import { DatabaseService } from './DatabaseService';
import { isValidHBSClass } from './NameValidator';

export interface CreateInstrumentData {
  entries: NameEntry[];
  instrument_source: string;
  hornbostel_sachs_class: string;
  image_file?: File | null;
  image_source?: string;
}

export interface CreateValidationResult {
  isValid: boolean;
  errors: Map<string, ValidationResult>;
}

const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
];
const MAX_IMAGE_SIZE = 2 * 1024 * 1024; // 2MB

export class CreateInstrumentValidator {
  private languages: WikidataLanguage[];

  constructor(languages: WikidataLanguage[] = []) {
    this.languages = languages;
  }

  /**
   * Validates Hornbostel-Sachs classification
   */
  validateHbsClassification(value: string): ValidationResult {
    if (!value || value.trim() === '') {
      return {
        isValid: false,
        message: 'Hornbostel-Sachs classification is required',
        type: 'error',
      };
    }

    if (!isValidHBSClass(value.trim())) {
      return {
        isValid: false,
        message:
          'Invalid format. Enter a valid HBS class (e.g., "11", "21.2", "311.121"). Must start with 1-5; only digits, dot, dash, and plus are permitted',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: '',
      type: 'success',
    };
  }

  /**
   * Validates language selection
   */
  validateLanguage(languageCode: string): ValidationResult {
    if (!languageCode || languageCode.trim() === '') {
      return {
        isValid: false,
        message: 'Language is required',
        type: 'error',
      };
    }

    const validLanguage = this.languages.some(
      (l) => l.wikidata_code === languageCode,
    );
    if (!validLanguage) {
      return {
        isValid: false,
        message: 'Please select a valid language from the list',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: '',
      type: 'success',
    };
  }

  /**
   * Validates that the user has selected a valid language from the datalist
   */
  validateLanguageInput(inputElement: HTMLInputElement): ValidationResult {
    const datalistId = inputElement.getAttribute('list');
    if (!datalistId) {
      return {
        isValid: false,
        message: 'Language datalist not found.',
        type: 'error',
      };
    }

    const datalist = document.getElementById(
      datalistId,
    ) as HTMLDataListElement | null;
    if (!datalist) {
      return {
        isValid: false,
        message: 'Language datalist not found.',
        type: 'error',
      };
    }

    const datalistOptions = datalist.querySelectorAll('option');
    const isValidSelection = Array.from(datalistOptions).some(
      (option) => (option as HTMLOptionElement).value === inputElement.value,
    );

    if (!isValidSelection) {
      return {
        isValid: false,
        message: 'Please select a valid language from the list.',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: 'Valid language selected.',
      type: 'success',
    };
  }

  /**
   * Validates instrument name
   */
  validateName(name: string): ValidationResult {
    if (!name || name.trim() === '') {
      return {
        isValid: false,
        message: 'Instrument name is required',
        type: 'error',
      };
    }

    if (name.trim().length < 2) {
      return {
        isValid: false,
        message: 'Name must be at least 2 characters',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: '',
      type: 'success',
    };
  }

  /**
   * Validates source field (must be filled and under 255 characters)
   */
  validateSource(source: string): ValidationResult {
    if (!source || source.trim() === '') {
      return {
        isValid: false,
        message: 'Source is required',
        type: 'error',
      };
    }
    if (source.trim().length > 255) {
      return {
        isValid: false,
        message: 'Source must be 255 characters or less.',
        type: 'error',
      };
    }
    return {
      isValid: true,
      message: '',
      type: 'success',
    };
  }

  /**
   * Validates image file
   */
  validateImageFile(file: File | null | undefined): ValidationResult {
    if (!file) {
      return {
        isValid: true,
        message: '',
        type: 'success',
      }; // Optional field
    }

    // Check file size
    if (file.size > MAX_IMAGE_SIZE) {
      return {
        isValid: false,
        message: 'Image file size must be less than 2MB',
        type: 'error',
      };
    }

    // Check file type
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      return {
        isValid: false,
        message: 'Invalid image type. Allowed: JPEG, PNG, GIF, WebP',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: 'Valid image file',
      type: 'success',
    };
  }

  /**
   * Validates image source field
   */
  validateImageSource(source: string): ValidationResult {
    if (!source || source.trim() === '') {
      return {
        isValid: false,
        message: 'Image source is required',
        type: 'error',
      };
    }

    if (source.length > 200) {
      return {
        isValid: false,
        message: 'Image source must be 200 characters or less',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: '',
      type: 'success',
    };
  }

  /**
   * Check for duplicate entries within the submission and against the database.
   * Returns a Map of field-specific errors for inline display.
   */
  async validateNoDuplicates(
    entries: NameEntry[],
  ): Promise<Map<string, ValidationResult>> {
    const errors = new Map<string, ValidationResult>();
    const seen = new Set<string>();

    // Check within submission (synchronous)
    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      if (!entry.language || !entry.name) continue;

      const key = `${entry.language}:${entry.name.toLowerCase()}`;
      if (seen.has(key)) {
        errors.set(`name${i + 1}`, {
          isValid: false,
          message: `Duplicate: "${entry.name}" already entered above`,
          type: 'error',
        });
      }
      seen.add(key);
    }

    // Check against database (asynchronous batch check)
    try {
      const result = await DatabaseService.checkDuplicateNames(entries);

      result.duplicates.forEach((duplicate) => {
        if (duplicate.exists) {
          // Find the original entry index to set error on correct field
          const originalIndex = entries.findIndex(
            (e) =>
              e.language === duplicate.language &&
              e.name.toLowerCase() === duplicate.name.toLowerCase(),
          );

          if (originalIndex !== -1) {
            const fieldId = `name${originalIndex + 1}`;
            errors.set(fieldId, {
              isValid: false,
              message: `An instrument with this name already exists in language "${duplicate.language}"`,
              type: 'error',
            });
          }
        }
      });
    } catch (error) {
      console.error('Failed to check for duplicate names:', error);
      // Don't block submission on API failure - backend will catch duplicates
    }

    return errors;
  }

  /**
   * Validates all form fields (async due to database duplicate checking)
   */
  async validateAll(
    data: CreateInstrumentData,
  ): Promise<CreateValidationResult> {
    const errors = new Map<string, ValidationResult>();
    let isValid = true;

    // Validate at least one entry exists
    if (!data.entries || data.entries.length === 0) {
      isValid = false;
      errors.set('nameRows', {
        isValid: false,
        message: 'At least one name entry is required',
        type: 'error',
      });
    }

    // Check for duplicates (within submission AND database)
    const duplicateErrors = await this.validateNoDuplicates(data.entries);
    if (duplicateErrors.size > 0) {
      isValid = false;
      duplicateErrors.forEach((error, fieldId) => {
        errors.set(fieldId, error);
      });
    }

    // Validate first entry (required)
    if (data.entries && data.entries.length > 0) {
      const firstEntry = data.entries[0];

      const langResult = this.validateLanguage(firstEntry.language);
      if (!langResult.isValid) {
        isValid = false;
        errors.set('language1', langResult);
      }

      const nameResult = this.validateName(firstEntry.name);
      if (!nameResult.isValid) {
        isValid = false;
        errors.set('name1', nameResult);
      }

      const sourceResult = this.validateSource(firstEntry.source);
      if (!sourceResult.isValid) {
        isValid = false;
        errors.set('source1', sourceResult);
      }
    }

    // Validate additional entries that have any data filled in
    if (data.entries && data.entries.length > 1) {
      for (let i = 1; i < data.entries.length; i++) {
        const entry = data.entries[i];
        const rowIndex = i + 1;

        // Only validate if any field has data
        const hasData =
          entry.language?.trim() || entry.name?.trim() || entry.source?.trim();

        if (hasData) {
          if (!entry.language?.trim()) {
            isValid = false;
            errors.set(`language${rowIndex}`, {
              isValid: false,
              message: 'Language is required for this entry',
              type: 'error',
            });
          } else {
            const langResult = this.validateLanguage(entry.language);
            if (!langResult.isValid) {
              isValid = false;
              errors.set(`language${rowIndex}`, langResult);
            }
          }

          if (!entry.name?.trim()) {
            isValid = false;
            errors.set(`name${rowIndex}`, {
              isValid: false,
              message: 'Name is required for this entry',
              type: 'error',
            });
          }

          // Validate source required and under 255 chars for each entry
          if (!entry.source?.trim()) {
            isValid = false;
            errors.set(`source${rowIndex}`, {
              isValid: false,
              message: 'Source is required for this entry',
              type: 'error',
            });
          } else if (entry.source.trim().length > 255) {
            isValid = false;
            errors.set(`source${rowIndex}`, {
              isValid: false,
              message: 'Source must be 255 characters or less.',
              type: 'error',
            });
          }
        }
      }
    }

    // Validate instrument source
    const instSourceResult = this.validateSource(data.instrument_source);
    if (!instSourceResult.isValid) {
      isValid = false;
      errors.set('instrumentSource', {
        ...instSourceResult,
        message: 'Instrument source is required',
      });
    }

    // Validate HBS classification
    const hbsResult = this.validateHbsClassification(
      data.hornbostel_sachs_class,
    );
    if (!hbsResult.isValid) {
      isValid = false;
      errors.set('hornbostelSachsClass', hbsResult);
    }

    // Validate image fields
    if (data.image_file) {
      const imageFileResult = this.validateImageFile(data.image_file);
      if (!imageFileResult.isValid) {
        isValid = false;
        errors.set('image', imageFileResult);
      }

      // Validate image source
      const imageSourceResult = this.validateImageSource(
        data.image_source || '',
      );
      if (!imageSourceResult.isValid) {
        isValid = false;
        errors.set('imageSource', imageSourceResult);
      }
    }

    return { isValid, errors };
  }

  /**
   * Displays feedback on a form field
   */
  displayFeedback(containerElement: Element, result: ValidationResult): void {
    const fieldContainer = containerElement as HTMLElement;
    const targetInput = fieldContainer.querySelector(
      'input',
    ) as HTMLInputElement;
    const validFeedback = fieldContainer.querySelector(
      '.valid-feedback',
    ) as HTMLElement;
    const invalidFeedback = fieldContainer.querySelector(
      '.invalid-feedback',
    ) as HTMLElement;

    if (!targetInput) return;

    if (result.isValid) {
      targetInput.classList.add('is-valid');
      targetInput.classList.remove('is-invalid');
      if (validFeedback && result.message) {
        validFeedback.textContent = result.message;
      }
    } else {
      targetInput.classList.add('is-invalid');
      targetInput.classList.remove('is-valid');
      if (invalidFeedback) {
        invalidFeedback.textContent = result.message;
      }
    }
  }

  /**
   * Clears validation state from a field
   */
  clearFeedback(containerElement: Element): void {
    const fieldContainer = containerElement as HTMLElement;
    const targetInput = fieldContainer.querySelector(
      'input',
    ) as HTMLInputElement;

    if (targetInput) {
      targetInput.classList.remove('is-valid', 'is-invalid');
    }
  }
}
