import { Modal } from 'bootstrap';
import { getCsrfToken } from '../../utils/cookies';

export class DeleteInstrumentManager {
  private instrumentUmilId: string | null = null;
  private instrumentName: string | null = null;
  private deleteInstrumentModal: HTMLElement;

  constructor() {
    this.deleteInstrumentModal = document.getElementById(
      'deleteInstrumentModal',
    )!;

    if (!this.deleteInstrumentModal) {
      throw new Error('Delete instrument modal not found');
    }
  }

  setupModalEvents(): void {
    this.deleteInstrumentModal.addEventListener('show.bs.modal', (event) => {
      this.handleModalShow(event);
    });
  }

  setupDeleteConfirmation(): void {
    const confirmBtn = document.getElementById('confirmDeleteInstrumentBtn');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => {
        this.executeDelete();
      });
    }
  }

  private handleModalShow(event: Event): void {
    const modalEvent = event as any;
    const button = modalEvent.relatedTarget;

    if (button) {
      this.instrumentUmilId = button.getAttribute('data-instrument-umil-id');
      this.instrumentName = button.getAttribute('data-instrument-name');

      this.populateModalData();
    }
  }

  private populateModalData(): void {
    const nameElement = this.deleteInstrumentModal.querySelector(
      '#deleteInstrumentName',
    );
    if (nameElement) {
      nameElement.textContent = this.instrumentName;
    }
  }

  private async executeDelete(): Promise<void> {
    if (!this.instrumentUmilId) {
      this.showModalError('Missing instrument identifier.');
      return;
    }

    const confirmBtn = document.getElementById(
      'confirmDeleteInstrumentBtn',
    ) as HTMLButtonElement;
    const originalText = confirmBtn?.innerHTML;
    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
    }

    this.hideModalError();

    try {
      const response = await fetch(
        `/api/instrument/${this.instrumentUmilId}/delete/`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
        },
      );

      const data = await response.json();

      if (data.status === 'success') {
        this.handleDeleteSuccess(data.redirect_url);
      } else {
        this.showModalError(data.message || 'Failed to delete instrument.');
        if (confirmBtn) {
          confirmBtn.disabled = false;
          confirmBtn.innerHTML = originalText;
        }
      }
    } catch (error) {
      this.showModalError(
        'An error occurred while deleting the instrument: ' +
          (error as Error).message,
      );
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalText;
      }
    }
  }

  private handleDeleteSuccess(redirectUrl?: string): void {
    const modalInstance = Modal.getInstance(this.deleteInstrumentModal);
    if (modalInstance) {
      modalInstance.hide();
    }

    window.location.href = redirectUrl || '/instruments/';
  }

  resetModal(): void {
    this.instrumentUmilId = null;
    this.instrumentName = null;

    const nameElement = this.deleteInstrumentModal.querySelector(
      '#deleteInstrumentName',
    );
    if (nameElement) {
      nameElement.textContent = '';
    }

    this.hideModalError();
  }

  private showModalError(message: string): void {
    const modalError = document.getElementById('deleteModalError');
    const modalErrorMessage = document.getElementById(
      'deleteModalErrorMessage',
    );

    if (modalError && modalErrorMessage) {
      modalErrorMessage.textContent = message;
      modalError.style.display = 'block';
      modalError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  private hideModalError(): void {
    const modalError = document.getElementById('deleteModalError');
    if (modalError) {
      modalError.style.display = 'none';
    }
  }
}
