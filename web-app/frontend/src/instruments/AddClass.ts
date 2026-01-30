import { Modal } from 'bootstrap';
import { NameValidator } from './helpers/NameValidator';

// Initialize NameValidator
const nameValidator = new NameValidator();

// Handle modal show event - populate instrument data
const addClassModal = document.getElementById('addClassModal');
addClassModal?.addEventListener('show.bs.modal', (event) => {
  const triggerButton = (event as any).relatedTarget;
  if (!triggerButton) return;

  const instrumentName = triggerButton.getAttribute('data-instrument-name');
  const instrumentWikidataId = triggerButton.getAttribute('data-instrument-wikidata-id');
  const instrumentPk = triggerButton.getAttribute('data-instrument-pk');
  const className = triggerButton.getAttribute('data-class-name');

  addClassModal.querySelector('#instrumentNameInModal')!.textContent = instrumentName;
  addClassModal.querySelector('#instrumentWikidataIdInModal')!.textContent = instrumentWikidataId;
  (addClassModal.querySelector('#instrumentPkInClassModal') as HTMLInputElement)!.value = instrumentPk;
  addClassModal.querySelector('#instrumentClassNameInModal')!.textContent = className;
});

// Reset modal on hide
addClassModal?.addEventListener('hide.bs.modal', () => {
  const form = document.getElementById('addClassForm') as HTMLFormElement;
  form?.reset();

  const classInput = document.getElementById('classInput') as HTMLInputElement;
  if (classInput) classInput.value = '';

  const container = classInput?.closest('.class-input');
  container?.classList.remove('is-valid', 'is-invalid');

  const resultMsg = document.getElementById('publishClassResults');
  if (resultMsg) resultMsg.textContent = '';
});

// Initialize DOM events
document.addEventListener('DOMContentLoaded', () => {
  const addClassForm = document.getElementById('addClassForm') as HTMLFormElement;
  if (!addClassForm) return;

  // Handle form submission
  addClassForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const classInputElem = document.getElementById('classInput') as HTMLInputElement;
    const classInput = classInputElem?.value?.trim() || '';
    const container = classInputElem.closest('.class-input');

    const validationResult = nameValidator.validateHBSClassInput(classInput);
    nameValidator.displayFeedback(container!, validationResult);

    if (!validationResult.isValid) return;

    // Show confirmation modal
    const confirmationModal = new Modal(document.getElementById('confirmationClassModal')!);
    confirmationModal.show();
  });

  // Handle confirm publish button
  const confirmBtn = document.getElementById('confirmPublishClassBtn');
  confirmBtn?.addEventListener('click', () => {
    const classInputElem = document.getElementById('classInput') as HTMLInputElement;
    const hbsClass = classInputElem.value.trim();
    const container = classInputElem.closest('.class-input');

    const validationResult = nameValidator.validateHBSClassInput(hbsClass);
    nameValidator.displayFeedback(container!, validationResult);
    if (!validationResult.isValid) return;

    const wikidataId = addClassModal?.querySelector('#instrumentWikidataIdInModal')?.textContent?.trim() || '';
    const instrumentPk = (document.getElementById('instrumentPkInClassModal') as HTMLInputElement).value;
    const resultMsg = document.getElementById('publishClassResults');

    const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement).value;

    fetch(`/instrument/${instrumentPk}/names/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        wikidata_id: wikidataId,
        hornbostel_sachs_class: hbsClass,
      }),
    })    
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'success') {
          // Close modals
          Modal.getInstance(document.getElementById('addClassModal'))?.hide();
          Modal.getInstance(document.getElementById('confirmationClassModal'))?.hide();
          window.location.reload();
        } else {
          if (resultMsg) {
            resultMsg.textContent = 'Error: ' + data.message;
            resultMsg.classList.add('text-danger');
          }
        }
      })
      .catch((err) => {
        if (resultMsg) {
          resultMsg.textContent = 'An error occurred while publishing: ' + err.message;
          resultMsg.classList.add('text-danger');
        }
      });
  });
});
