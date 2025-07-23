document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('toggle-language-table');
  const hiddenRows = document.querySelectorAll('.extra-language-row');

  if (toggleBtn) {
    let expanded = false;

    toggleBtn.addEventListener('click', () => {
      expanded = !expanded;
      hiddenRows.forEach((row) => {
        row.classList.toggle('d-none', !expanded);
      });
      toggleBtn.textContent = expanded
        ? 'View fewer languages'
        : 'View all languages';
    });
  }
});
