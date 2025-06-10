// Make this file a module to allow global augmentation
export {};

// Add a type declaration for window.bootstrap
declare global {
  interface Window {
    bootstrap: any;
  }
}

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new (window as any).bootstrap.Tooltip(tooltipTriggerEl),
);
