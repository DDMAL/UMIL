document.addEventListener('DOMContentLoaded', function () {
  const editButtons = document.querySelectorAll('.btn-edit');
  const cancelButtons = document.querySelectorAll('.btn-cancel');
  const publishButtons = document.querySelectorAll('.btn-publish');

  editButtons.forEach((button) => {
    button.addEventListener('click', function (this: HTMLElement) {
      const parentTd = this.closest('td');
      const flexContainer = parentTd.querySelector('.d-flex') as HTMLElement;
      const viewField = flexContainer.querySelector(
        '.view-field',
      ) as HTMLElement;
      const editField = flexContainer.querySelector(
        '.edit-field',
      ) as HTMLElement;
      const cancelBtn = flexContainer.querySelector(
        '.btn-cancel',
      ) as HTMLElement;
      const publishBtn = flexContainer.querySelector(
        '.btn-publish',
      ) as HTMLElement;

      viewField.classList.add('d-none');
      editField.classList.remove('d-none');
      cancelBtn.classList.remove('d-none');
      publishBtn.classList.remove('d-none');
      this.style.display = 'none';
    });
  });

  cancelButtons.forEach((button) => {
    button.addEventListener('click', function (this: HTMLElement) {
      const parentTd = this.closest('td');
      const flexContainer = parentTd.querySelector('.d-flex') as HTMLElement;
      const viewField = flexContainer.querySelector(
        '.view-field',
      ) as HTMLElement;
      const editField = flexContainer.querySelector(
        '.edit-field',
      ) as HTMLElement;
      const editBtn = flexContainer.querySelector('.btn-edit') as HTMLElement;
      const publishBtn = flexContainer.querySelector(
        '.btn-publish',
      ) as HTMLElement;

      viewField.classList.remove('d-none');
      editField.classList.add('d-none');
      editBtn.style.display = 'inline-block';
      publishBtn.classList.add('d-none');
      this.classList.add('d-none');
    });
  });

  publishButtons.forEach((button) => {
    button.addEventListener('click', function (this: HTMLElement) {
      const parentTd = this.closest('td');
      const flexContainer = parentTd.querySelector('.d-flex') as HTMLElement;
      const viewField = flexContainer.querySelector(
        '.view-field',
      ) as HTMLElement;
      const editField = flexContainer.querySelector(
        '.edit-field',
      ) as HTMLInputElement;
      const editBtn = flexContainer.querySelector('.btn-edit') as HTMLElement;
      const cancelBtn = flexContainer.querySelector(
        '.btn-cancel',
      ) as HTMLElement;

      const newValue = editField.value;
      // TODO: request to update the value on the server
      viewField.textContent = newValue;
      viewField.classList.remove('d-none');
      editField.classList.add('d-none');
      editBtn.style.display = 'inline-block';
      this.classList.add('d-none');
      cancelBtn.classList.add('d-none');
    });
  });
});
