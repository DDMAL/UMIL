(function () {
  // Minimal deterministic Google Translate stub for E2E testing
  window.google = window.google || {};
  window.google.translate = window.google.translate || {};

  // Cookie management
  function setCookie(name, value) {
    document.cookie = name + '=' + value + '; path=/; SameSite=Lax';
  }

  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp(
        '(?:^|; )' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)',
      ),
    );
    return match ? decodeURIComponent(match[1]) : '';
  }

  // Apply language change and update DOM
  function applyLanguage(langCode) {
    if (langCode === 'fr') {
      setCookie('googtrans', '/en/fr');
      document.documentElement.setAttribute('lang', 'fr');
    } else if (langCode === 'en' || langCode === '') {
      setCookie('googtrans', '');
      document.documentElement.setAttribute('lang', 'en');
    }
  }

  // Initialize language attribute from cookie immediately
  (function initLangAttribute() {
    const googtrans = getCookie('googtrans');
    if (googtrans && googtrans.includes('/fr')) {
      document.documentElement.setAttribute('lang', 'fr');
    } else {
      document.documentElement.setAttribute('lang', 'en');
    }
  })();

  // TranslateElement constructor
  function TranslateElement(options, elementId) {
    const self = this;

    // Function to create and inject the widget
    function createWidget() {
      const container = document.getElementById(elementId);
      if (!container) {
        // Retry if container not found
        setTimeout(createWidget, 50);
        return;
      }

      // Clear any existing content
      container.innerHTML = '';

      // Create widget structure
      const gadget = document.createElement('div');
      gadget.className = 'goog-te-gadget';

      const select = document.createElement('select');
      select.className = 'goog-te-combo';
      select.setAttribute('aria-label', 'Language Translate Widget');

      // Add options
      const optionData = [
        { value: '', text: 'Select Language' },
        { value: 'en', text: 'English' },
        { value: 'fr', text: 'French' },
      ];

      optionData.forEach((data) => {
        const option = document.createElement('option');
        option.value = data.value;
        option.text = data.text;
        select.appendChild(option);
      });

      // Set initial value from cookie
      const currentCookie = getCookie('googtrans');
      if (currentCookie && currentCookie.includes('/fr')) {
        select.value = 'fr';
      } else {
        select.value = 'en';
      }

      // Handle change events
      select.addEventListener('change', function () {
        const selectedValue = this.value;
        applyLanguage(selectedValue);
      });

      // Append to DOM
      gadget.appendChild(select);
      container.appendChild(gadget);
    }

    // Create widget immediately if DOM is ready, otherwise wait
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createWidget);
    } else {
      // Use setTimeout to ensure it runs after current call stack
      setTimeout(createWidget, 0);
    }
  }

  // Static properties
  TranslateElement.InlineLayout = {
    HORIZONTAL: 0,
    SIMPLE: 1,
    VERTICAL: 2,
  };

  // Export to window
  window.google.translate.TranslateElement = TranslateElement;
})();
