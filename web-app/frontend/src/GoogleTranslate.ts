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

const pageLanguage = document.querySelector('#google_translate_element');

function googleTranslateElementInit() {
  new google.translate.TranslateElement(
    {
      pageLanguage: 'en',
      layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL,
    },
    'google_translate_element',
  );

  const googleSelect = document.getElementsByClassName(
    'goog-te-combo',
  )[0] as HTMLSelectElement;
  googleSelect.classList.add('btn', 'p-0', 'm-0', 'h-100');

  const parent = googleSelect.parentElement;
  parent.classList.add('h-100', 'd-flex', 'align-items-center');

  const grandparent = parent.parentElement;
  grandparent.classList.add('h-100', 'd-flex', 'align-items-center');
}

// Export the initialization function so it's globally accessible
window.googleTranslateElementInit = googleTranslateElementInit;

// Add the type definition to the Window interface
declare global {
  interface Window {
    googleTranslateElementInit: typeof googleTranslateElementInit;
  }
}

// Force this file to be treated as a module
export {};
