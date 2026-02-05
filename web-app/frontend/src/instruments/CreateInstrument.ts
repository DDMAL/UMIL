import { WikidataLanguage } from './Types';
import { CreateInstrumentValidator } from './helpers/CreateInstrumentValidator';
import { CreateInstrumentManager } from './helpers/CreateInstrumentManager';
import { getLanguages } from './utils';

const languages: WikidataLanguage[] = getLanguages();

let validator: CreateInstrumentValidator;
let manager: CreateInstrumentManager;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  // Initialize services
  validator = new CreateInstrumentValidator(languages);
  manager = new CreateInstrumentManager(languages, validator);

  // Initialize form and setup event listeners
  manager.initializeForm();
  manager.setupAddRowButton();
  manager.setupFormSubmission();
  manager.setupHbsValidation();
  manager.setupImageFieldToggle();
});
