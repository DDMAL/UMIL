document.addEventListener('DOMContentLoaded', function (): void {
  const dropdownBtn: HTMLElement = document.getElementById(
    'language-dropdown-btn',
  )!;
  const dropdownMenu: HTMLElement = document.getElementById(
    'language-dropdown-list',
  )!;
  const dropdownItems: NodeListOf<HTMLElement> = dropdownMenu.querySelectorAll(
    '.umil-dropdown-item',
  );
  let searchQuery: string = '';

  // Attach keydown event listeners once
  dropdownBtn.addEventListener('keydown', handleKeydown);
  dropdownMenu.addEventListener('keydown', handleKeydown);

  // Listen for when the dropdown is hidden
  const instrumentLanguageElement: HTMLElement | null = document.getElementById(
    'instrument-language-element',
  );
  if (instrumentLanguageElement) {
    instrumentLanguageElement.addEventListener(
      'hide.bs.dropdown',
      function (): void {
        searchQuery = ''; // Clear search when hidden
      },
    );
  }

  // Handle key press events only when the dropdown is visible
  function handleKeydown(event: KeyboardEvent): void {
    const isDropdownVisible: boolean = dropdownMenu.classList.contains('show');
    if (!isDropdownVisible) return;

    // Backspace: Remove last character in search query
    if (event.key === 'Backspace') {
      searchQuery = searchQuery.slice(0, -1);
    } else if (event.key.length === 1 && event.key.match(/[a-zA-Z]/)) {
      // Add the new letter to the search query
      searchQuery += event.key.toLowerCase();
    }

    // Filter the dropdown items based on the search query
    const matchingItems: HTMLElement[] = Array.from(dropdownItems).filter(
      (item: HTMLElement): boolean => {
        const languageName: string =
          item.textContent?.trim().toLowerCase() || '';
        const isMatch: boolean = languageName.startsWith(searchQuery);
        return isMatch;
      },
    );

    // If there are matching items, highlight the first match
    if (matchingItems.length > 0) {
      const targetItem: HTMLElement = matchingItems[0]; // First matched item
      targetItem.focus(); // Focus on the matching item
      dropdownMenu.scrollTop = targetItem.offsetTop - dropdownMenu.offsetTop; // Scroll to the matching item
    }
  }
});
