// Retrieves the list of languages from the #languages-json element
export function getLanguages() {
  const el = document.getElementById('languages-json');
  if (!el) {
    console.error('languages-json not found');
    return [];
  }
  return JSON.parse(el.textContent || '[]');
}
