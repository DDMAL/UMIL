import { NameValidator } from './helpers/NameValidator';
import { DeleteNameManager } from './helpers/DeleteNameManager';

let nameValidator: NameValidator;
let deleteNameManager: DeleteNameManager;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  // Initialize services
  nameValidator = new NameValidator();
  deleteNameManager = new DeleteNameManager(nameValidator);

  // Setup event listeners
  deleteNameManager.setupModalEvents();
  deleteNameManager.setupDeleteConfirmation();
});

// Reset the modal when hidden
document
  .getElementById('deleteNameModal')
  ?.addEventListener('hide.bs.modal', () => deleteNameManager?.resetModal());
