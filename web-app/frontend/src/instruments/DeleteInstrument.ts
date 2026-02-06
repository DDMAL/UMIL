import { DeleteInstrumentManager } from './helpers/DeleteInstrumentManager';

let deleteInstrumentManager: DeleteInstrumentManager;

document.addEventListener('DOMContentLoaded', function () {
  deleteInstrumentManager = new DeleteInstrumentManager();

  deleteInstrumentManager.setupModalEvents();
  deleteInstrumentManager.setupDeleteConfirmation();
});

document
  .getElementById('deleteInstrumentModal')
  ?.addEventListener('hide.bs.modal', () =>
    deleteInstrumentManager?.resetModal(),
  );
