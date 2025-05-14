document.addEventListener('DOMContentLoaded', function () {
  const dropdownBtn = document.getElementById('language-dropdown-btn');
  const dropdownMenu = document.getElementById('language-dropdown-list');
  const dropdownItems = dropdownMenu.querySelectorAll('.umil-dropdown-item');
  let searchQuery = '';

  // Attach keydown event listeners once
  dropdownBtn.addEventListener('keydown', handleKeydown);
  dropdownMenu.addEventListener('keydown', handleKeydown);

  // Listen for when the dropdown is hidden
  document
    .getElementById('instrument-language-element')
    .addEventListener('hide.bs.dropdown', function () {
      searchQuery = ''; // Clear search when hidden
    });

  // Handle key press events only when the dropdown is visible
  function handleKeydown(event) {
    const isDropdownVisible = dropdownMenu.classList.contains('show');
    if (!isDropdownVisible) return;

    // Backspace: Remove last character in search query
    if (event.key === 'Backspace') {
      searchQuery = searchQuery.slice(0, -1);
    } else if (event.key.length === 1 && event.key.match(/[a-zA-Z]/)) {
      // Add the new letter to the search query
      searchQuery += event.key.toLowerCase();
    }

    // Filter the dropdown items based on the search query
    const matchingItems = Array.from(dropdownItems).filter((item) => {
      const languageName = item.textContent.trim().toLowerCase();
      const isMatch = languageName.startsWith(searchQuery);
      return isMatch;
    });

    // If there are matching items, highlight the first match
    if (matchingItems.length > 0) {
      const targetItem = matchingItems[0]; // First matched item
      targetItem.focus(); // Focus on the matching item
      dropdownMenu.scrollTop = targetItem.offsetTop - dropdownMenu.offsetTop; // Scroll to the matching item
    }
  }
});
