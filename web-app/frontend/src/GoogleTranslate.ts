import { setCookie, readCookie } from './utils/cookies';

declare namespace google {
  namespace translate {
    class TranslateElement {
      constructor(
        options: {
          pageLanguage: string;
          layout: any;
        },
        elementId: string,
      );

      static InlineLayout: {
        HORIZONTAL: any;
        SIMPLE: any;
        VERTICAL: any;
      };
    }
  }
}

function googleTranslateElementInit() {
  // Wait for DOM if still loading
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', googleTranslateElementInit);
    return;
  }

  // Check prerequisites and retry if not ready
  if (
    !google?.translate ||
    !document.getElementById('google_translate_element')
  ) {
    setTimeout(googleTranslateElementInit, 100);
    return;
  }

  try {
    new google.translate.TranslateElement(
      {
        pageLanguage: 'en',
        layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL,
      },
      'google_translate_element',
    );
    customizeGoogleTranslate();
  } catch (error) {
    console.error('Google Translate initialization failed:', error);
    setTimeout(googleTranslateElementInit, 200);
  }
}

function customizeGoogleTranslate() {
  const googleSelect = document.querySelector(
    '.goog-te-combo',
  ) as HTMLSelectElement;
  if (!googleSelect || googleSelect.options.length === 0) {
    setTimeout(customizeGoogleTranslate, 100);
    return;
  }
  googleSelect.classList.add('p-0', 'm-0', 'h-100');
  googleSelect.parentElement?.classList.add(
    'h-100',
    'd-flex',
    'align-items-center',
  );
  googleSelect.parentElement?.parentElement?.classList.add(
    'h-100',
    'd-flex',
    'align-items-center',
  );

  if (readCookie('frSite') === 'true') {
    setGTLanguage(googleSelect, 'fr');
  } else if (readCookie('enSite') === 'true') {
    clearGTLanguage();
  }

  // Set up observer to watch for Google Translate widget changes
  watchGTDefaultText(googleSelect);
}

// Watch for the default text of the Google Translate widget to be "Select Language"
// and set it to "English"
function watchGTDefaultText(googleSelect: HTMLSelectElement) {
  const updateText = () => {
    const option = Array.from(googleSelect.options).find((opt) =>
      opt.text.toLowerCase().includes('select language'),
    );
    if (option) option.text = 'English';
  };

  updateText(); // Initial check

  const observer = new MutationObserver(() => updateText());
  observer.observe(googleSelect, { childList: true, subtree: true });

  const interval = setInterval(updateText, 1000);
  setTimeout(() => {
    observer.disconnect();
    clearInterval(interval);
  }, 30000);
}

function setGTLanguage(googleSelect: HTMLSelectElement, language: string) {
  googleSelect.value = language;
  googleSelect.dispatchEvent(new Event('change'));
}

function clearGTLanguage() {
  // Clear the Google Translate cookie
  setCookie('googtrans', '', '/', window.location.hostname);
  setCookie('frSite', 'false', '/', window.location.hostname);
  setCookie('enSite', 'false', '/', window.location.hostname);

  // Force a page reload to ensure translation is completely cleared
  window.location.reload();
}

function getGTLanguage(googleSelect: HTMLSelectElement) {
  return readCookie('googtrans');
}

// Export the initialization function so it's globally accessible for backwards compatibility
window.googleTranslateElementInit = googleTranslateElementInit;

function setupSiteLanguageListeners() {
  // Wait for DOM if still loading
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupSiteLanguageListeners);
    return;
  }

  // Set up French site button listener
  const frSiteBtn = document.getElementById('fr-site-btn');
  if (frSiteBtn) {
    frSiteBtn.addEventListener('click', (event) => {
      // Prevent default link behavior temporarily
      event.preventDefault();

      // Set cookies for French site
      setCookie('frSite', 'true', '/', window.location.hostname);
      setCookie('enSite', 'false', '/', window.location.hostname);

      // Get the href from the parent anchor element and redirect
      const parentLink = frSiteBtn.closest('a') as HTMLAnchorElement;
      if (parentLink && parentLink.href) {
        window.location.href = parentLink.href;
      }
    });
  }

  // Set up English site button listener
  const enSiteBtn = document.getElementById('en-site-btn');
  if (enSiteBtn) {
    enSiteBtn.addEventListener('click', (event) => {
      // Prevent default link behavior temporarily
      event.preventDefault();

      // Set cookies for English site
      setCookie('enSite', 'true', '/', window.location.hostname);
      setCookie('frSite', 'false', '/', window.location.hostname);

      // Get the href from the parent anchor element and redirect
      const parentLink = enSiteBtn.closest('a') as HTMLAnchorElement;
      if (parentLink && parentLink.href) {
        window.location.href = parentLink.href;
      }
    });
  }
}

// Start the initialization process
googleTranslateElementInit();

// Set up site language button listeners
setupSiteLanguageListeners();

// Add the type definition to the Window interface
declare global {
  interface Window {
    googleTranslateElementInit: typeof googleTranslateElementInit;
  }
}

// Force this file to be treated as a module
export {};
