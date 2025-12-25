// Static list of suggestions in the autocomplete-list div,


const staticSuggestions = ['Piano', 'Violin', 'Flute', 'Trumpet', 'Drums'];

function renderSuggestionList(
  listElement: HTMLElement,
  suggestions: string[],
  input: HTMLInputElement,
  form: HTMLFormElement,
) {
  listElement.innerHTML = '';
  suggestions.forEach((suggestion) => {
    const item = document.createElement('div');
    item.className = 'list-group-item list-group-item-action';
    item.textContent = suggestion;
    item.style.cursor = 'pointer';

    // On click, set input value and submit the form
    item.addEventListener('click', () => {
      input.value = suggestion;
      form.submit();
    });
    listElement.appendChild(item);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById(
    'instrument-search',
  ) as HTMLInputElement | null;
  const list = document.getElementById(
    'autocomplete-list',
  ) as HTMLElement | null;
  
  const form = input?.closest('form') as HTMLFormElement | null;

  if (!input || !list || !form) return;

  renderSuggestionList(list, staticSuggestions, input, form);

  function showList() {
    list.classList.remove('d-none');
  }

  function hideList() {
    list.classList.add('d-none');
  }

  // Show suggestions when user types more than 2 chars
  input.addEventListener('input', () => {
    if (input.value.trim().length > 1) {
      showList();
    } else {
      hideList();
    }
  });

  // Hide when clicking outside
  document.addEventListener('click', (event) => {
    if (event.target !== input && !list.contains(event.target as Node)) {
      hideList();
    }
  });
});
