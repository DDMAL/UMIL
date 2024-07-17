document.addEventListener('DOMContentLoaded', function () {
  const editButtons = document.querySelectorAll('.btn.edit');
  const cancelButtons = document.querySelectorAll('.btn.cancel');
  const publishButtons = document.querySelectorAll('.btn.publish');

  editButtons.forEach((button) => {
    button.addEventListener('click', function () {
      const parentTd = this.closest('td');
      parentTd.querySelector('.view-field').style.display = 'none';
      parentTd.querySelector('.edit-field').style.display = 'inline-block';
      parentTd.querySelector('.btn.cancel').style.display = 'inline-block';
      parentTd.querySelector('.btn.publish').style.display = 'inline-block';
      this.style.display = 'none';
    });
  });

  cancelButtons.forEach((button) => {
    button.addEventListener('click', function () {
      const parentTd = this.closest('td');
      parentTd.querySelector('.view-field').style.display = 'inline';
      parentTd.querySelector('.edit-field').style.display = 'none';
      parentTd.querySelector('.btn.edit').style.display = 'inline-block';
      parentTd.querySelector('.btn.publish').style.display = 'none';
      this.style.display = 'none';
    });
  });

  publishButtons.forEach((button) => {
    button.addEventListener('click', function () {
      const parentTd = this.closest('td');
      const newValue = parentTd.querySelector('.edit-field').value;
      // TODO: request to update the value on the server
      parentTd.querySelector('.view-field').textContent = newValue;
      parentTd.querySelector('.view-field').style.display = 'inline';
      parentTd.querySelector('.edit-field').style.display = 'none';
      parentTd.querySelector('.btn.edit').style.display = 'inline-block';
      this.style.display = 'none';
      parentTd.querySelector('.btn.cancel').style.display = 'none';
    });
  });
});
