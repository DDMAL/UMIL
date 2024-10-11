// Get the modal element
var addNameModal = document.getElementById('addNameModal');

addNameModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget;
  var instrumentName = button.getAttribute('data-instrument-name');
  var instrumentWikidataId = button.getAttribute('data-instrument-wikidata-id');
  var instrumentNameInModal = addNameModal.querySelector(
    '#instrumentNameInModal'
  );
  instrumentNameInModal.textContent = instrumentName;

  var instrumentWikidataIdInModal = addNameModal.querySelector(
    '#instrumentWikidataIdInModal'
  );
  instrumentWikidataIdInModal.textContent = instrumentWikidataId;
});

// the number of rows in the modal
let rowIndex = 1;

// Function to validate that the user has selected a valid language from the datalist
function isValidLanguage(inputElement) {
  const datalistId = inputElement.getAttribute('list');
  const datalist = document.getElementById(datalistId);
  const options = datalist.querySelectorAll('option');

  // Check if the input value matches any option value in the datalist
  for (let option of options) {
    if (option.value === inputElement.value) {
      return true; // Valid language selected
    }
  }
  return false; // Invalid language input
}

// Function to check if a name already exists in Wikidata for the given language
async function checkNameInWikidata(wikidataId, languageCode, languageLabel) {
  const sparqlQuery = `
    SELECT ?nameLabel WHERE {
      wd:${wikidataId} rdfs:label ?nameLabel .
      FILTER(LANG(?nameLabel) = "${languageCode}")
    } LIMIT 1
  `;

  const endpointUrl = 'https://query.wikidata.org/sparql';
  const queryUrl = `${endpointUrl}?query=${encodeURIComponent(
    sparqlQuery
  )}&format=json`;

  try {
    const response = await fetch(queryUrl);
    const data = await response.json();

    if (data.results.bindings.length > 0) {
      return { exists: true, name: data.results.bindings[0].nameLabel.value };
    } else {
      return { exists: false };
    }
  } catch (error) {
    console.error('Error querying Wikidata:', error);
    throw new Error('Wikidata query failed');
  }
}

// Reusable function to create a new row
function createRow(index) {
  const row = document.createElement('div');
  row.classList.add('row', 'mb-1', 'name-row');

  // Create datalist options dynamically using the global languages variable
  let datalistOptions = languages
    .map(
      (language) => `
      <option value="${language.wikidata_code}">${language.autonym} - ${language.en_label}</option>
  `
    )
    .join('');

  row.innerHTML = `
    <div class="col-md-2 language-input">
      <label for="language${index}" class="form-label-sm">Language</label>
      <input list="languages${index}" class="form-control" id="language${index}" name="language[]" placeholder="Type to search" required />
      <datalist id="languages${index}">
        ${datalistOptions}
      </datalist>
      <div class="valid-feedback">This instrument does not have a name in this language yet. You can add a new name.</div>
      <div class="invalid-feedback">This instrument already has a name in this language.</div>
    </div>
    <div class="col-md-2 name-input">
      <label for="name${index}" class="form-label-sm">Name</label>
      <input type="text" class="form-control" id="name${index}" name="name[]" placeholder="Enter name" required />
      <div class="valid-feedback"></div>
      <div class="invalid-feedback"></div>
    </div>
    <div class="col-md-2 source-input">
      <label for="source${index}" class="form-label-sm">Source</label>
      <input type="text" class="form-control" id="source${index}" name="source[]" placeholder="Enter source" required />
      <div class="valid-feedback"></div>
      <div class="invalid-feedback"></div>
    </div>
    <div class="col-md-2 description-input">
      <label for="description${index}" class="form-label-sm">Description</label>
      <input type="text" class="form-control" id="description${index}" name="description[]" placeholder="Enter description" />
      <div class="valid-feedback"></div>
      <div class="invalid-feedback"></div>
    </div>
    <div class="col-md-2 alias-input">
      <label for="alias${index}" class="form-label-sm">Also known as</label>
      <input type="text" class="form-control" id="alias${index}" name="alias[]" placeholder="Enter alias" />
      <div class="valid-feedback"></div>
      <div class="invalid-feedback"></div>
    </div>
    <div class="col-md-1 d-flex align-items-center">
      <button type="button" class="btn btn-outline-danger btn-sm remove-row-btn">Remove</button>
    </div>
  `;

  // Add event listener for remove button
  row.querySelector('.remove-row-btn').addEventListener('click', function () {
    row.remove();
    updateRemoveButtons(); // Ensure correct behavior when rows are removed
  });

  return row;
}

// Function to update remove button visibility based on the number of rows
function updateRemoveButtons() {
  const rows = document.querySelectorAll('.name-row');
  rows.forEach((row, index) => {
    const removeButton = row.querySelector('.remove-row-btn');
    // Show the remove button only if there are more than one row
    if (rows.length > 1) {
      removeButton.style.display = 'inline-block';
    } else {
      removeButton.style.display = 'none'; // Hide the button if only one row remains
    }
  });
}

// Function to validate and check all rows on form submission
document
  .getElementById('addNameForm')
  .addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent form submission

    const nameRows = document.querySelectorAll('.name-row');
    let allValid = true;
    let publishResults = ''; // Collect the results for confirmation

    // Iterate over each row and check if the name already exists in Wikidata
    for (let row of nameRows) {
      const languageInput = row.querySelector('input[list]');
      const nameInput = row.querySelector('.name-input input[type="text"]');
      const sourceInput = row.querySelector('.source-input input[type="text"]');
      const descriptionInput = row.querySelector(
        '.description-input input[type="text"]'
      );
      const aliasInput = row.querySelector('.alias-input input[type="text"]');

      const languageCode = languageInput.value;
      const selectedOption = row.querySelector(
        `option[value="${languageCode}"]`
      );
      const languageLabel = selectedOption ? selectedOption.textContent : '';

      // get feedback elements for valid and invalid inputs respectively for language and name
      const languageFeedbackValid = row.querySelector(
        '.language-input .valid-feedback'
      );
      const languageFeedbackInvalid = row.querySelector(
        '.language-input .invalid-feedback'
      );
      const nameFeedbackInvalid = row.querySelector(
        '.name-input .invalid-feedback'
      );
      const sourceFeedbackInvalid = row.querySelector(
        '.source-input .invalid-feedback'
      );

      const wikidataId = document
        .getElementById('instrumentWikidataIdInModal')
        .textContent.trim();

      if (!isValidLanguage(languageInput)) {
        languageInput.classList.add('is-invalid');
        languageFeedbackInvalid.textContent =
          'Please select a valid language from the list.';
        allValid = false;
        continue;
      }

      try {
        const result = await checkNameInWikidata(
          wikidataId,
          languageCode,
          languageLabel
        );
        if (result.exists) {
          languageInput.classList.add('is-invalid');
          languageInput.classList.remove('is-valid');
          languageFeedbackInvalid.textContent = `This instrument already has a name in ${languageLabel} (${languageCode}): ${result.name}`;
          allValid = false;
        } else {
          languageInput.classList.add('is-valid');
          languageInput.classList.remove('is-invalid');
          languageFeedbackValid.textContent = `This instrument does not have a name in ${languageLabel} (${languageCode}) yet. You can add a new name.`;

          // check if name is empty
          if (nameInput.value.trim() === '') {
            nameInput.classList.add('is-invalid');
            nameInput.classList.remove('is-valid');
            nameFeedbackInvalid.textContent =
              'Please enter a name for this instrument in the selected language.';
            allValid = false;
          } else {
            nameInput.classList.add('is-valid');
            nameInput.classList.remove('is-invalid');
          }

          // check if source is empty
          if (sourceInput.value.trim() === '') {
            sourceInput.classList.add('is-invalid');
            sourceInput.classList.remove('is-valid');
            sourceFeedbackInvalid.textContent =
              'Please enter the source of this name.';
            allValid = false;
          } else {
            sourceInput.classList.add('is-valid');
            sourceInput.classList.remove('is-invalid');
          }

          // Add the result to the confirmation message
          publishResults += `<br />${languageLabel} (${languageCode}): ${nameInput.value}; Source: ${sourceInput.value}; Description: ${descriptionInput.value}; Alias: ${aliasInput.value}`;
        }
      } catch (error) {
        displayMessage(
          'There was an error checking Wikidata. Please try again later.',
          'danger'
        );
        return; // Stop further processing
      }
    }

    // If all rows are valid, show the confirmation modal
    if (allValid) {
      document.getElementById(
        'publishResults'
      ).innerHTML = `You will publish the following:<br />${publishResults}`;
      const confirmationModal = new bootstrap.Modal(
        document.getElementById('confirmationModal')
      );
      confirmationModal.show();
    }
  });

// Function to reset the modal and ensure only one row is present
function resetModal() {
  const nameRows = document.getElementById('nameRows');
  nameRows.innerHTML = ''; // Clear all rows
  nameRows.appendChild(createRow(1)); // Add initial row
  updateRemoveButtons(); // Ensure remove buttons are updated on reset
  rowIndex = 1; // Reset row index
}

// Fetch languages when the modal is loaded
document.addEventListener('DOMContentLoaded', async () => {
  resetModal();
});

// Add a new row when the 'Add another row' button is clicked
document.getElementById('addRowBtn').addEventListener('click', function () {
  rowIndex++;
  const nameRows = document.getElementById('nameRows');
  nameRows.appendChild(createRow(rowIndex));
  updateRemoveButtons(); // Update remove buttons after adding a new row
});

// Reset the modal when hidden
document
  .getElementById('addNameModal')
  .addEventListener('hide.bs.modal', resetModal);

// Function to handle confirm publish action
document
  .getElementById('confirmPublishBtn')
  .addEventListener('click', function () {
    const wikidataId = document
      .getElementById('instrumentWikidataIdInModal')
      .textContent.trim();
    const entries = [];

    // Collect the data to publish
    const nameRows = document.querySelectorAll('.name-row');
    nameRows.forEach((row) => {
      const languageInput = row.querySelector('input[list]');
      const nameInput = row.querySelector('.name-input input[type="text"]');
      const sourceInput = row.querySelector('.source-input input[type="text"]');
      const descriptionInput = row.querySelector(
        '.description-input input[type="text"]'
      );
      const aliasInput = row.querySelector('.alias-input input[type="text"]');

      const languageCode = languageInput.value;
      const nameValue = nameInput.value;
      const sourceValue = sourceInput.value;
      const descriptionValue = descriptionInput.value;
      const aliasValue = aliasInput.value;

      if (
        languageCode &&
        nameValue &&
        sourceValue &&
        descriptionValue &&
        aliasValue
      ) {
        entries.push({
          language: languageCode,
          name: nameValue,
          source: sourceValue,
          description: descriptionValue,
          alias: aliasValue,
        });
      }
    });

    // Check if the user wants to publish to Wikidata
    const publishToWikidata = document.getElementById(
      'publishToWikidataCheckbox'
    ).checked;

    // Publish data to our database and then to Wikidata
    fetch('/publish_name/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')
          .value,
      },
      body: JSON.stringify({
        wikidata_id: wikidataId,
        entries: entries,
        publish_to_wikidata: publishToWikidata,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          alert('Data published successfully!');
          // Close both modals
          const addNameModal = bootstrap.Modal.getInstance(
            document.getElementById('addNameModal')
          );
          const confirmationModal = bootstrap.Modal.getInstance(
            document.getElementById('confirmationModal')
          );

          if (addNameModal) {
            addNameModal.hide(); // Close the 'Add Name' modal
          }

          if (confirmationModal) {
            confirmationModal.hide(); // Close the 'Confirmation' modal
          }
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch((error) => {
        alert('An error occurred while publishing the data: ' + error.message);
      });
  });
