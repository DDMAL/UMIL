import { WikidataLanguage, ValidationResult } from '../Types';
import { WikidataService } from './WikidataService';

export class NameValidator {
  private languages: WikidataLanguage[];

  constructor(languages: WikidataLanguage[] = []) {
    this.languages = languages;
  }

  /**
   * Validates that the user has selected a valid language from the datalist
   */
  validateLanguage(inputElement: HTMLInputElement): ValidationResult {
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
   * Validates that the name field is not empty
   */
  validateNameField(
    nameInput: string,
    minLength = 2,
    maxLength = 50,
  ): ValidationResult {
    const trimmed = nameInput.trim();

    if (trimmed === '') {
      return {
        isValid: false,
        message:
          'Please enter a name for this instrument in the selected language.',
        type: 'error',
      };
    }

    if (trimmed.length < minLength) {
      return {
        isValid: false,
        message: `Name must be at least ${minLength} characters long.`,
        type: 'error',
      };
    }

    if (trimmed.length > maxLength) {
      return {
        isValid: false,
        message: `Name cannot exceed ${maxLength} characters.`,
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
   * Validates that the source field is not empty
   */
  validateSource(
    sourceInput: string,
    minLength = 2,
    maxLength = 255,
  ): ValidationResult {
    const trimmed = sourceInput.trim();

    if (trimmed === '') {
      return {
        isValid: false,
        message: 'Please enter the source of this name.',
        type: 'error',
      };
    }

    if (trimmed.length < minLength) {
      return {
        isValid: false,
        message: `Name must be at least ${minLength} characters long.`,
        type: 'error',
      };
    }

    if (trimmed.length > maxLength) {
      return {
        isValid: false,
        message: `Name cannot exceed ${maxLength} characters.`,
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
   * Validates that we have a valid name ID for deletion
   */
  validateNameId(nameId: string | null): ValidationResult {
    if (!nameId || nameId.trim() === '') {
      return {
        isValid: false,
        message: 'No instrument name ID provided for deletion.',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: 'Valid instrument name ID provided.',
      type: 'success',
    };
  }

  /**
   * Validates that required modal data is present for deletion
   */
  validateModalData(
    name: string | null,
    language: string | null,
    source: string | null,
  ): ValidationResult {
    if (!name || !language || !source) {
      return {
        isValid: false,
        message: 'Missing required instrument data for deletion.',
        type: 'error',
      };
    }

    return {
      isValid: true,
      message: 'All required data is present.',
      type: 'success',
    };
  }

  /**
   * Validates that the deletion operation can proceed
   */
  validateDeletion(
    nameId: string | null,
    name: string | null,
    language: string | null,
    source: string | null,
  ): ValidationResult {
    const idValidation = this.validateNameId(nameId);
    if (!idValidation.isValid) {
      return idValidation;
    }

    const dataValidation = this.validateModalData(name, language, source);
    if (!dataValidation.isValid) {
      return dataValidation;
    }

    return {
      isValid: true,
      message: 'Ready to delete instrument name.',
      type: 'success',
    };
  }

  /**
   * Validates a complete instrument name including Wikidata checks
   */
  async validateName(
    languageCode: string,
    nameInput: string,
    sourceInput: string,
    wikidataId: string,
  ): Promise<{
    isValid: boolean;
    languageResult: ValidationResult;
    nameResult: ValidationResult;
    sourceResult: ValidationResult;
    languageDescription: string;
  }> {
    // Find the selected language
    const selectedLanguage = this.languages.find(
      (language) => language.wikidata_code === languageCode,
    );
    const languageDescription = selectedLanguage
      ? `${selectedLanguage.autonym} - ${selectedLanguage.en_label}`
      : '';

    // Basic validation
    const nameResult = this.validateNameField(nameInput);
    const sourceResult = this.validateSource(sourceInput);

    let languageResult: ValidationResult = {
      isValid: true,
      message: '',
      type: 'success',
    };

    let isAlias = false;

    // If basic validation passes, check Wikidata
    if (nameResult.isValid && sourceResult.isValid && selectedLanguage) {
      try {
        // Check if name already exists on Wikidata
        const nameExistsResult = await WikidataService.checkIfNameExists(
          wikidataId,
          languageCode,
          nameInput,
        );

        if (nameExistsResult.exists) {
          return {
            isValid: false,
            languageResult: {
              isValid: false,
              message: `This instrument already has this name on Wikidata in ${languageCode} (${languageDescription}).`,
              type: 'error',
            },
            nameResult: {
              isValid: false,
              message: `This instrument already has this name on Wikidata in ${languageCode} (${languageDescription}).`,
              type: 'error',
            },
            sourceResult,
            languageDescription,
          };
        }

        languageResult = {
          isValid: true,
          message: 'Valid language selected.',
          type: 'success',
        };

        const wikidataValidationResult: ValidationResult = {
          isValid: true,
          message: 'You can add this as a new name.',
          type: 'success',
        };

        return {
          isValid: true,
          languageResult,
          nameResult: wikidataValidationResult,
          sourceResult,
          languageDescription,
        };
      } catch (error) {
        return {
          isValid: false,
          languageResult: {
            isValid: false,
            message: 'Error checking Wikidata. Please try again later.',
            type: 'error',
          },
          nameResult: {
            isValid: false,
            message: 'Error checking Wikidata. Please try again later.',
            type: 'error',
          },
          sourceResult,
          languageDescription,
        };
      }
    }

    return {
      isValid: nameResult.isValid && sourceResult.isValid,
      languageResult,
      nameResult,
      sourceResult,
      languageDescription,
    };
  }

  /**
   * Updates the UI feedback for a form element
   */
  displayFeedback(containerElement: Element, result: ValidationResult): void {
    const fieldContainer = containerElement as HTMLElement;

    // Find the actual input element within the container
    const targetInput = fieldContainer.querySelector(
      'input',
    ) as HTMLInputElement;
    const validFeedback = fieldContainer.querySelector(
      '.valid-feedback',
    ) as HTMLElement;
    const invalidFeedback = fieldContainer.querySelector(
      '.invalid-feedback',
    ) as HTMLElement;

    if (!targetInput) {
      console.warn(
        'No input element found in container for validation feedback',
      );
      return;
    }

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
}
