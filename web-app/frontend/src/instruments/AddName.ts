import { Modal } from 'bootstrap';
import { NameValidator } from './helpers/NameValidator';
import { AddNameManager } from './helpers/AddNameManager';
import { NameRowManager } from './helpers/NameRowManager';
import { getLanguages } from './utils';

const languages = getLanguages();

let nameRowManager: NameRowManager;
let nameValidator: NameValidator;
let addNameManager: AddNameManager;

// Handle modal show event - populate instrument data
const addNameModal = document.getElementById('addNameModal');
addNameModal.addEventListener('show.bs.modal', function (event) {
  const triggerButton = (event as any).relatedTarget;
  if (triggerButton) {
    const instrumentName = triggerButton.getAttribute('data-instrument-name');
    const instrumentUmilId = triggerButton.getAttribute(
      'data-instrument-umil-id',
    );
    const instrumentWikidataId = triggerButton.getAttribute(
      'data-instrument-wikidata-id',
    );

    addNameModal.querySelector('#instrumentNameInModal').textContent =
      instrumentName;
    addNameModal.querySelector('#instrumentUmilIdInModal').textContent =
      instrumentUmilId;
    addNameModal.querySelector('#instrumentWikidataIdInModal').textContent =
      instrumentWikidataId || '';
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
  nameRowManager = new NameRowManager(languages);
  nameValidator = new NameValidator(languages);
  addNameManager = new AddNameManager(nameRowManager, nameValidator);

  // Setup event listeners
  addNameManager.setupAddRowButton();
  addNameManager.setupFormSubmission();
  addNameManager.setupPublishConfirmation();

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
