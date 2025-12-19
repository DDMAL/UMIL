import { setCookie, readCookie, deleteCookie } from './utils/cookies';

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
    attachGTLanguageListener();
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

function attachGTLanguageListener() {
  const googleSelect =
    document.querySelector<HTMLSelectElement>('.goog-te-combo');

  if (!googleSelect) {
    setTimeout(attachGTLanguageListener, 100);
    return;
  }

  // Wait to GT set its current value (from another tab)
  setTimeout(() => {
    if (googleSelect.value) {
      updateLanguageButtons(googleSelect.value);
    }
  }, 500);

  // Update when user changes language
  googleSelect.addEventListener('change', () => {
    if (!googleSelect.value) return;
    updateLanguageButtons(googleSelect.value);
  });
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
  // Try deleting with both possible domain formats (localhost and .localhost)
  // Safari requires exact domain match, and Google Translate may set cookies with either format
  const hostname = window.location.hostname;
  deleteCookie('googtrans', { path: '/', domain: hostname });

  // Also try with leading dot (for subdomain cookies)
  // Only do this if hostname is not an IP address
  if (!/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
    deleteCookie('googtrans', { path: '/', domain: `.${hostname}` });
  }

  // Also try without any domain (for cookies set without domain attribute)
  deleteCookie('googtrans', { path: '/' });

  setCookie('frSite', 'false', {});
  setCookie('enSite', 'false', {});

  // Force a page reload to ensure translation is completely cleared
  window.location.reload();
}

function getGTLanguage(googleSelect: HTMLSelectElement) {
  return readCookie('googtrans');
}

function updateLanguageButtons(langCode: string) {
  let displayName = langCode;

  // Convert code → English display name
  if (typeof Intl?.DisplayNames === 'function') {
    const dn = new Intl.DisplayNames(['en'], { type: 'language' });
    displayName = dn.of(langCode) ?? langCode;
  }

  document
    .querySelectorAll<HTMLAnchorElement>('a.dynamic-language-link')
    .forEach((link) => {
      try {
        const url = new URL(link.href, window.location.origin);
        // Put DISPLAY NAME in URL
        url.searchParams.set('language', displayName);
        link.href = url.pathname + url.search + url.hash;
      } catch {}

      let btn = link.querySelector<HTMLButtonElement>('.en-site-btn');

      if (btn) {
        // Remove cookie Listeners
        const newBtn = btn.cloneNode(true) as HTMLButtonElement;
        btn.replaceWith(newBtn);
        btn = newBtn;
      }
      if (!btn) return;

      btn.textContent = `Visit ${displayName} Site`;
    });
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
  const frSiteBtns = document.querySelectorAll('.fr-site-btn');
  frSiteBtns.forEach((frSiteBtn) => {
    frSiteBtn.addEventListener('click', (event) => {
      // Prevent default link behavior temporarily
      event.preventDefault();

      // Set cookies for French site
      setCookie('frSite', 'true', {});
      setCookie('enSite', 'false', {});

      // Get the href from the parent anchor element and redirect
      const parentLink = frSiteBtn.closest('a') as HTMLAnchorElement;
      if (parentLink && parentLink.href) {
        window.location.href = parentLink.href;
      }
    });
  });

  // Set up English site button listener
  const enSiteBtns = document.querySelectorAll('.en-site-btn');
  enSiteBtns.forEach((enSiteBtn) => {
    enSiteBtn.addEventListener('click', (event) => {
      // Prevent default link behavior temporarily
      event.preventDefault();

      // Set cookies for English site
      setCookie('enSite', 'true', {});
      setCookie('frSite', 'false', {});

      // Get the href from the parent anchor element and redirect
      const parentLink = enSiteBtn.closest('a') as HTMLAnchorElement;
      if (parentLink && parentLink.href) {
        window.location.href = parentLink.href;
      }
    });
  });
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
