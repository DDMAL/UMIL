async function fetchSuggestions(query: string): Promise<string[]> {
  if (!query.trim()) return [];
  try {
    const response = await fetch(
      `/instruments/suggest/?q=${encodeURIComponent(query)}`
    );
    if (!response.ok) return [];
    const data = await response.json();
    return Array.isArray(data.suggestions) ? data.suggestions : [];
  } catch {
    return [];
  }
}

function renderSuggestionList(
  listElement: HTMLElement,
  suggestions: string[],
  input: HTMLInputElement,
  form: HTMLFormElement,
) {
  listElement.innerHTML = '';
  if (suggestions.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'list-group-item text-muted';
    empty.textContent = 'No suggestions';
    listElement.appendChild(empty);
    return;
  }
  suggestions.forEach((suggestion) => {
    const item = document.createElement('div');
    item.className = 'list-group-item list-group-item-action';
    item.textContent = suggestion;

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

  function showList() {
    list.classList.remove('d-none');
  }

  function hideList() {
    list.classList.add('d-none');
  }

  let debounceTimer: number | null = null;

  input.addEventListener('input', () => {
    const val = input.value.trim();
    if (debounceTimer) {
      window.clearTimeout(debounceTimer);
    }
    if (val.length > 1) {
      debounceTimer = window.setTimeout(async () => {
        const suggestions = await fetchSuggestions(val);
        renderSuggestionList(list, suggestions, input, form);
        showList();
      }, 150);
    } else {
      hideList();
      list.innerHTML = '';
    }
  });

  document.addEventListener('click', (event) => {
    if (event.target !== input && !list.contains(event.target as Node)) {
      hideList();
    }
  });
});
