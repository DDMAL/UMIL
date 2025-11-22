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

  // Check if Google Translate widget already exists and remove it
  // This is needed for back/forward navigation
  const existingWidget = document.querySelector('.goog-te-banner-frame');
  if (existingWidget) {
    existingWidget.remove();
  }

  // Clear any existing Google Translate elements
  const existingElements = document.querySelectorAll(
    '.goog-te-combo, .goog-te-gadget',
  );
  existingElements.forEach((element) => element.remove());

  try {
    new google.translate.TranslateElement(
      {
        pageLanguage: 'en',
        layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL,
      },
      'google_translate_element',
    );
    customizeGoogleTranslate();
    syncGTLanguageToURL();

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
  if (readCookie('enSite') === 'true') {
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

// Sync the Google Translate language to the URL
function syncGTLanguageToURL() {
  const googleSelect = document.querySelector<HTMLSelectElement>('.goog-te-combo');
  if (!googleSelect) {
    setTimeout(syncGTLanguageToURL, 100);
    return;
  }

  googleSelect.addEventListener('change', () => {
    const selectedLang = googleSelect.value;

    // Update URL
    const currentUrl = new URL(window.location.href);
    if (currentUrl.searchParams.get('language') !== selectedLang) {
      currentUrl.searchParams.set('language', selectedLang);
      window.history.replaceState({}, '', currentUrl.toString());
    }

    // Reload when Google Translate finish translation
    waitForGoogleTranslate(() => {
      // Do not reload if a cookie is set
      if (readCookie('frSite') === 'true' || readCookie('enSite') === 'true') return;
      window.location.reload();
    });

  });

  // Update all links on page
  let langCode = googleSelect.value;
  // Fallback to language param if select value is blank
  if (!langCode) {
    const langFromUrl = new URL(window.location.href).searchParams.get('language');
    if (langFromUrl) langCode = langFromUrl;
  }

  if (langCode) {
    updateLinksWithLanguage(langCode);
  }
}

function updateLinksWithLanguage(langCode: string) {
  // This updates all navbar links and add language param
  // Also, updates links in elements with id=dynamic-language-link with language param
  // It renames id=en-site-btn to avoid setting cookies
  // It renames the content "Visit English Site" to the set language

  const updateLink = (link: HTMLAnchorElement) => {
    try {
      const url = new URL(link.getAttribute('href') || '', window.location.origin);
      url.searchParams.set('language', langCode);
      link.setAttribute('href', url.pathname + url.search + url.hash);
    } catch { /* skip broken links */ }
  };

  // Update only #navbarMenu a.nav-link links
  document.querySelectorAll<HTMLAnchorElement>('#navbarMenu a.nav-link').forEach(link => {
    updateLink(link);
  });

  // Only update a.dynamic-language-link if the language is not French
  if (!langCode.toLowerCase().startsWith('fr')) {
    document.querySelectorAll<HTMLAnchorElement>('a.dynamic-language-link').forEach(link => {
      updateLink(link);
      // Rename #en-site-btn and set its text (if present inside dynamic-language-link)
      const enBtn = link.querySelector('#en-site-btn') as HTMLButtonElement | null;
      if (enBtn) {
        // Rename the id to avoid cookies
        enBtn.id = 'en-site-btn-renamed';

        // Set button content to match the selected language for the "Visit Site" button
        let languageName = langCode;
        try {
          if (typeof Intl !== 'undefined' && typeof Intl.DisplayNames === 'function') {
            try {
              // Get English display names for languages
              const displayNames = new Intl.DisplayNames(['en'], { type: 'language' });

              const readable = displayNames.of(langCode);

              if (readable) {
                // Capitalize the language name
                languageName = readable.replace(/\b\w/g, c => c.toUpperCase());
              }
            } catch {}
          }
        } catch {}
        enBtn.textContent = `Visit ${languageName} Site`;
      }
    });
  }
}


// Detect when Google Translate finishes applying translation
function waitForGoogleTranslate(callback: () => void) {
  const html = document.documentElement;

  // If already translated execute callback
  if (html.classList.contains('translated-ltr') || 
      html.classList.contains('translated-rtl')) {
    callback();
    return;
  }

  const observer = new MutationObserver(() => {
    if (html.classList.contains('translated-ltr') || 
        html.classList.contains('translated-rtl')) {
      observer.disconnect();
      callback();
    }
  });

  observer.observe(html, { attributes: true, attributeFilter: ['class'] });
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

// Handle browser navigation events (back/forward buttons)
function handleNavigationEvents() {
  // Listen for popstate events (back/forward navigation)
  window.addEventListener('popstate', () => {
    // Small delay to ensure DOM is ready after navigation
    setTimeout(() => {
      googleTranslateElementInit();
    }, 100);
  });

  // Listen for pageshow events (handles both initial load and back/forward cache)
  window.addEventListener('pageshow', (event) => {
    // Reinitialize if the page was loaded from cache (back/forward navigation)
    if (event.persisted) {
      setTimeout(() => {
        googleTranslateElementInit();
      }, 100);
    }
  });
}

// Set up navigation event listeners
handleNavigationEvents();

// Add the type definition to the Window interface
declare global {
  interface Window {
    googleTranslateElementInit: typeof googleTranslateElementInit;
  }
}

// Force this file to be treated as a module
export {};
