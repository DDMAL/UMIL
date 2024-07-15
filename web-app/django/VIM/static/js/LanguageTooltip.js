const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"], [data-bs-toggle="dropdown"]'
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);
