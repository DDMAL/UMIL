document.addEventListener('DOMContentLoaded', function () {
  const dropdownBtn = document.getElementById('language-dropdown-btn');
  const dropdownMenu = document.getElementById('language-dropdown-list');
  const dropdownItems = dropdownMenu.querySelectorAll('.umil-dropdown-item');
  let searchQuery = '';

  let dropdownVisible = false; // Flag to track visibility

  // Listen for when the dropdown is shown
  document
    .getElementById('instrument-language-element')
    .addEventListener('show.bs.dropdown', function () {
      dropdownVisible = true;

      // Enable keydown event listener for searching
      enableSearch();
    });

  // Listen for when the dropdown is hidden
  document
    .getElementById('instrument-language-element')
    .addEventListener('hide.bs.dropdown', function () {
      dropdownVisible = false;

      // Clear the search query and disable keydown event listener
      searchQuery = '';
      disableSearch();
    });

  // Function to enable keyboard input for search
  function enableSearch() {
    dropdownBtn.addEventListener('keydown', handleKeydown);
    dropdownMenu.addEventListener('keydown', handleKeydown);
  }

  // Function to disable keyboard input for search
  function disableSearch() {
    dropdownBtn.removeEventListener('keydown', handleKeydown);
    dropdownMenu.removeEventListener('keydown', handleKeydown);
  }

  // Handle key press events only when the dropdown is visible
  function handleKeydown(event) {
    if (!dropdownVisible) return; // Don't process key events if dropdown is hidden

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
