import { Modal } from 'bootstrap';
import { NameValidator } from './NameValidator';

export class DeleteNameManager {
  private nameId: string | null = null;
  private instrumentPk: string | null = null;
  private nameValidator: NameValidator;
  private deleteNameModal: HTMLElement;

  constructor(nameValidator: NameValidator) {
    this.nameValidator = nameValidator;
    this.deleteNameModal = document.getElementById('deleteNameModal');

    if (!this.deleteNameModal) {
      throw new Error('Delete name modal not found');
    }
  }

  /**
   * Sets up modal event listeners
   */
  setupModalEvents(): void {
    this.deleteNameModal.addEventListener('show.bs.modal', (event) => {
      this.handleModalShow(event);
    });
  }

  /**
   * Sets up delete confirmation button event listener
   */
  setupDeleteConfirmation(): void {
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener('click', () => {
        this.executeDelete();
      });
    }
  }

  /**
   * Handles modal show event - populate instrument data
   */
  private handleModalShow(event: Event): void {
    const modalEvent = event as any;
    const button = modalEvent.relatedTarget;

    if (button) {
      const language = button.getAttribute('data-instrument-language');
      const name = button.getAttribute('data-instrument-name');
      const source = button.getAttribute('data-instrument-source');
      this.instrumentPk = button.getAttribute('data-instrument-pk');
      this.nameId = button.getAttribute('data-instrument-id');

      // Validate the data before populating
      const validationResult = this.nameValidator.validateModalData(
        name,
        language,
        source,
      );

      if (validationResult.isValid) {
        this.populateModalData(name, source, language);
      } else {
        console.error('Invalid modal data:', validationResult.message);
        // Could show error feedback here
      }
    }
  }

  /**
   * Populates modal with instrument data
   */
  private populateModalData(
    name: string,
    source: string,
    language: string,
  ): void {
    // Populate header
    const nameHeaderElement = this.deleteNameModal.querySelector(
      '#instrumentNameInModalHeader',
    );
    if (nameHeaderElement) nameHeaderElement.textContent = name;

    // Populate body
    const nameElement = this.deleteNameModal.querySelector(
      '#instrumentNameInModal',
    );
    const sourceElement = this.deleteNameModal.querySelector(
      '#instrumentSourceInModal',
    );
    const languageElement = this.deleteNameModal.querySelector(
      '#instrumentLanguageInModal',
    );

    if (nameElement) nameElement.textContent = name;
    if (sourceElement) sourceElement.textContent = source;
    if (languageElement) languageElement.textContent = language;
  }

  /**
   * Executes the delete operation
   */
  private async executeDelete(): Promise<void> {
    // Validate before deletion
    const validationResult = this.nameValidator.validateNameId(this.nameId);

    if (!validationResult.isValid) {
      alert('Error: ' + validationResult.message);
      return;
    }

    try {
      const csrfToken = this.getCsrfToken();

      const response = await fetch(`/instrument/${this.instrumentPk}/names/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          instrument_name_id: this.nameId,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        this.handleDeleteSuccess();
      } else {
        alert('Error: ' + data.message);
      }
    } catch (error) {
      alert('An error occurred while deleting the data: ' + error.message);
    }
  }

  /**
   * Handles successful deletion
   */
  private handleDeleteSuccess(): void {
    // Close the modal
    const deleteNameModalInstance = Modal.getInstance(this.deleteNameModal);
    if (deleteNameModalInstance) {
      deleteNameModalInstance.hide();
    }

    // Reload the page to reflect changes
    window.location.reload();
  }

  /**
   * Gets CSRF token from the page
   */
  private getCsrfToken(): string {
    const csrfTokenElement = document.querySelector(
      '[name=csrfmiddlewaretoken]',
    ) as HTMLInputElement;
    if (!csrfTokenElement) {
      throw new Error('CSRF token not found');
    }
    return csrfTokenElement.value;
  }

  /**
   * Resets the modal to its initial state
   */
  resetModal(): void {
    this.nameId = null;

    // Clear header
    const nameHeaderElement = this.deleteNameModal.querySelector(
      '#instrumentNameInModalHeader',
    );
    if (nameHeaderElement) nameHeaderElement.textContent = '';

    // Clear modal content
    const nameElement = this.deleteNameModal.querySelector(
      '#instrumentNameInModal',
    );
    const sourceElement = this.deleteNameModal.querySelector(
      '#instrumentSourceInModal',
    );
    const languageElement = this.deleteNameModal.querySelector(
      '#instrumentLanguageInModal',
    );

    if (nameElement) nameElement.textContent = '';
    if (sourceElement) sourceElement.textContent = '';
    if (languageElement) languageElement.textContent = '';
  }

  /**
   * Gets the current instrument name ID
   */
  getCurrentNameId(): string | null {
    return this.nameId;
  }
}
