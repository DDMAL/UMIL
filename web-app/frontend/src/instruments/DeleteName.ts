// Get the modal element
var deleteNameModal = document.getElementById('deleteNameModal');
let instrumentNameId = null; // Variable to store the instrument name ID

// Handle modal show event
deleteNameModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget;
  if (button != undefined) {
    var instrumentNameLanguage = button.getAttribute(
      'data-instrument-language',
    );
    var instrumentName = button.getAttribute('data-instrument-name');
    var instrumentSource = button.getAttribute(
      'data-instrument-source');
    instrumentNameId = button.getAttribute(
      'data-instrument-id');

    deleteNameModal.querySelector('#instrumentNameInModal').textContent =
      instrumentName;
    deleteNameModal.querySelector('#instrumentSourceInModal').textContent =
      instrumentSource;
    deleteNameModal.querySelector('#instrumentLanguageInModal').textContent =
      instrumentNameLanguage;
  }

});

document.getElementById('confirmDeleteBtn').addEventListener('click', function () {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  console.log('Deleting instrument name with ID:', instrumentNameId);

  // Send the request to publish
  fetch(`/delete-name/`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({
      instrument_name_id: instrumentNameId,
      // publish_to_wikidata: publishToWikidata,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === 'success') {
        // Close both modals
        const deleteNameModal = bootstrap.Modal.getInstance(
          document.getElementById('deleteNameModal'),
        );

        if (deleteNameModal) {
          deleteNameModal.hide(); // Close the 'Add Name' modal
        }
      } else {
        alert('Error: ' + data.message);
      }
    })
    .catch((error) => {
      alert('An error occurred while deleting the data: ' + error.message);
    });

    window.location.reload(); // Reload the page to reflect changes
});