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

    // Apply styling after widget renders
    setTimeout(() => {
      const googleSelect = document.querySelector(
        '.goog-te-combo',
      ) as HTMLSelectElement;
      if (googleSelect) {
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
      }
    }, 50);
  } catch (error) {
    console.error('Google Translate initialization failed:', error);
    setTimeout(googleTranslateElementInit, 200);
  }
}

// Export the initialization function so it's globally accessible for backwards compatibility
window.googleTranslateElementInit = googleTranslateElementInit;

// Start the initialization process
googleTranslateElementInit();

// Add the type definition to the Window interface
declare global {
  interface Window {
    googleTranslateElementInit: typeof googleTranslateElementInit;
  }
}

// Force this file to be treated as a module
export {};
