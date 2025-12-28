import { Modal } from 'bootstrap';
import { WikidataLanguage, NameEntry } from './Types';
import { NameValidator } from './helpers/NameValidator';
import { AddNameManager } from './helpers/AddNameManager';

declare const languages: WikidataLanguage[];

let nameValidator: NameValidator;
let addNameManager: AddNameManager;
let isPublishing = false;

// Handle modal show event - populate instrument data
const addNameModal = document.getElementById('addNameModal');
addNameModal.addEventListener('show.bs.modal', function (event) {
  const triggerButton = (event as any).relatedTarget;
  if (triggerButton) {
    const instrumentName = triggerButton.getAttribute('data-instrument-name');
    const instrumentWikidataId = triggerButton.getAttribute(
      'data-instrument-wikidata-id',
    );
    const instrumentPk = triggerButton.getAttribute('data-instrument-pk');

    addNameModal.querySelector('#instrumentNameInModal').textContent =
      instrumentName;
    addNameModal.querySelector('#instrumentWikidataIdInModal').textContent =
      instrumentWikidataId;
    (
      addNameModal.querySelector('#instrumentPkInModal') as HTMLInputElement
    ).value = instrumentPk;
  }
});

// Reset modal on close
document
  .getElementById('addNameModal')
  .addEventListener('hide.bs.modal', function () {
    localStorage.removeItem('addNameFormData');
  });

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  // Initialize services
  nameValidator = new NameValidator(languages);
  addNameManager = new AddNameManager(languages, nameValidator);

  // Setup form event listeners
  addNameManager.setupAddRowButton();
  addNameManager.setupFormSubmission();

  // Handle stored form data
  const storedFormData = localStorage.getItem('addNameFormData');
  if (storedFormData) {
    const addNameModalInstance = new Modal(
      document.getElementById('addNameModal'),
    );
    addNameModalInstance.show();
    addNameManager.restoreFormData(storedFormData);
  } else {
    addNameManager.resetModal();
  }
});

// Reset the modal when hidden
document
  .getElementById('addNameModal')
  .addEventListener('hide.bs.modal', () => addNameManager.resetModal());

// Publishing functionality
// Handle confirm publish action
document
  .getElementById('confirmPublishBtn')
  .addEventListener('click', function () {
    if (isPublishing) return;
    isPublishing = true;

    const confirmBtn = document.getElementById(
      'confirmPublishBtn',
    ) as HTMLButtonElement;

    // Disable button and rename it
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Saving…';

    const wikidataId = document
      .getElementById('instrumentWikidataIdInModal')
      .textContent.trim();

    const instrumentPk = (
      document.getElementById('instrumentPkInModal') as HTMLInputElement
    ).value;

    const entries: NameEntry[] = [];

    // Collect form data from all rows
    const nameRows = document.querySelectorAll('.name-row');
    nameRows.forEach((currentRow) => {
      const languageInput = currentRow.querySelector(
        'input[list]',
      ) as HTMLInputElement;
      const nameInput = currentRow.querySelector(
        '.name-input input[type="text"]',
      ) as HTMLInputElement;
      const sourceInput = currentRow.querySelector(
        '.source-input input[type="text"]',
      ) as HTMLInputElement;

      entries.push({
        language: languageInput.value,
        name: nameInput.value,
        source: sourceInput.value,
      });
    });

    // Get CSRF token and publish to backend
    const csrfToken = (
      document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement
    ).value;

    fetch(`/instrument/${instrumentPk}/names/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        wikidata_id: wikidataId,
        entries: entries,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          // Close modals
          const addNameModal = Modal.getInstance(
            document.getElementById('addNameModal'),
          );
          const confirmationModal = Modal.getInstance(
            document.getElementById('confirmationModal'),
          );

          addNameModal?.hide();
          confirmationModal?.hide();

          // Reload to reflect changes
          window.location.reload();
        } else {
          alert('Error: ' + data.message);

          // Restore state on failure
          isPublishing = false;
          confirmBtn.disabled = false;
          confirmBtn.textContent = 'Confirm';
        }
      })
      .catch((error) => {
        alert('An error occurred while publishing: ' + error.message);

        // Restore state on failure
        isPublishing = false;
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Confirm';
      });
  });
