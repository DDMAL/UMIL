import { Modal } from 'bootstrap';

// Function to handle confirm publish action
document
  .getElementById('confirmUploadBtn')
  .addEventListener('click', function () {
    // Get the CSRF token
    const csrftoken = (
      document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement
    ).value;

    console.log('Confirm Upload button clicked');

    fetch("/get-wikidata-access-token/")
      .then((response) => response.json())
      .then((data) => {
        if (data.access_token) {
          console.log('Wikidata access token retrieved successfully');
     
          // Send the request to publish
          fetch(`/edit-wikidata/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.status === 'success') {
                const uploadConfirmationModal = Modal.getInstance(
                  document.getElementById('uploadConfirmationModal'),
                );
                if (uploadConfirmationModal) {
                  uploadConfirmationModal.hide(); // Close the 'Confirmation' modal
                }

                // reload the page to reflect changes
                window.location.reload();
              } else {
                alert('Error: ' + data.message);
              }
            })
            .catch((error) => {
              alert('An error occurred while publishing the data: ' + error.message);
            });
        } else {
          console.error('Failed to retrieve Wikidata access token:', data.message);
          window.location.href = '/oauth/authorize/';
          return;
        }
      })
      .catch((error) => {
        console.error('Error fetching Wikidata access token:', error);
      });
  });