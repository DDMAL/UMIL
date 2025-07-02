// Get the modal element
var addNameModal = document.getElementById('addNameModal');

// Handle modal show event
addNameModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget;
  if (button != undefined) {
    var instrumentName = button.getAttribute('data-instrument-name');
    var instrumentWikidataId = button.getAttribute(
      'data-instrument-wikidata-id',
    );

    addNameModal.querySelector('#instrumentNameInModal').textContent =
      instrumentName;
    addNameModal.querySelector('#instrumentWikidataIdInModal').textContent =
      instrumentWikidataId;
  }

});

// Function to store form data
function storeFormData() {
  const storedData = {};
  storedData['instrumentName'] = document.getElementById(
    'instrumentNameInModal',
  ).textContent;
  storedData['wikidata_id'] = document.getElementById(
    'instrumentWikidataIdInModal',
  ).textContent;
  storedData['nameRows'] = [];
  document.querySelectorAll('.name-row').forEach((row) => {
    const rowData = {
      language: row.querySelector('.language-input input').value,
      name: row.querySelector('.name-input input').value,
      source: row.querySelector('.source-input input').value,
      // description: row.querySelector('.description-input input').value,
      // alias: row.querySelector('.alias-input input').value,
    };
    storedData['nameRows'].push(rowData);
  });
  localStorage.setItem('addNameFormData', JSON.stringify(storedData));
}

// Function to restore form data
function restoreFormData(storedData) {
  const form = document.getElementById('addNameForm');
  const parsedData = JSON.parse(storedData);
  // Restore main form values
  for (const key in parsedData) {
    if (form.elements[key]) {
      form.elements[key].value = parsedData[key];
    }
  }

  // Restore wikidata_id, publish_to_wikidata
  document.getElementById('instrumentNameInModal').textContent =
    parsedData['instrumentName'];
  document.getElementById('instrumentWikidataIdInModal').textContent =
    parsedData['wikidata_id'];

  // Restore dynamically added rows
  const nameRowsContainer = document.getElementById('nameRows');
  nameRowsContainer.innerHTML = ''; // Clear existing rows

  if (parsedData['nameRows'] && parsedData['nameRows'].length > 0) {
    parsedData['nameRows'].forEach((rowData, index) => {
      const newRow = createRow(index + 1);
      nameRowsContainer.appendChild(newRow);
      newRow.querySelector('.language-input input').value = rowData.language;
      newRow.querySelector('.name-input input').value = rowData.name;
      newRow.querySelector('.source-input input').value = rowData.source;
      // newRow.querySelector('.description-input input').value =
      //   rowData.description;
      // newRow.querySelector('.alias-input input').value = rowData.alias;
    });
  }

  // Check rows
  const nameRows = document.querySelectorAll('.name-row');
  nameRows.forEach((row) => {
    const languageInput = row.querySelector('input[list]');
    const nameInput = row.querySelector('.name-input input[type="text"]');
    const sourceInput = row.querySelector('.source-input input[type="text"]');
  });

}

// Reset modal on close
document
  .getElementById('addNameModal')
  .addEventListener('hide.bs.modal', function () {
    localStorage.removeItem('addNameFormData');
  });

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
async function isAlias(wikidataId, languageCode, languageLabel) {
  const sparqlQuery = `
    SELECT ?nameLabel WHERE {
      wd:${wikidataId} rdfs:label ?nameLabel .
      FILTER(LANG(?nameLabel) = "${languageCode}")
    } LIMIT 1
  `;

  const endpointUrl = 'https://query.wikidata.org/sparql';
  const queryUrl = `${endpointUrl}?query=${encodeURIComponent(
    sparqlQuery,
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

// Function to check if a name already exists in Wikidata for the given language
async function existOnWikidata(wikidataId, languageCode, languageLabel, nameInput) {
  console.log(languageCode)
  console.log(nameInput)

  const sparqlQuery = `
     SELECT ?nameLabel WHERE {
      wd:${wikidataId} (rdfs:label|skos:altLabel) ?nameLabel .
      FILTER(LANG(?nameLabel) = "${languageCode}" && CONTAINS(LCASE(?nameLabel),"${nameInput.toLowerCase()}"))
    } LIMIT 1
  `;

  const endpointUrl = 'https://query.wikidata.org/sparql';
  const queryUrl = `${endpointUrl}?query=${encodeURIComponent(
    sparqlQuery,
  )}&format=json`;

  try {
    const response = await fetch(queryUrl);
    const data = await response.json();

    console.log('Wikidata query result:', data);

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
  `,
    )
    .join('');

  row.innerHTML = `
    <div class="col-md-2 language-input">
      <label for="language${index}" class="form-label-sm">Language</label>
      <input list="languages${index}" class="form-control" id="language${index}" name="language[]" placeholder="Type to search" required />
      <datalist id="languages${index}">
        ${datalistOptions}
      </datalist>
      <div class="valid-feedback"></div>
      <div class="invalid-feedback"></div>
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
    <input type="hidden" class="alias-status" id="alias${index}" name="alias[]" values="false" />
    <div class="col-md-1 d-flex align-items-end">
      <button type="button" class="btn delete btn-sm remove-row-btn">Remove</button>
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

    // // Iterate over each row and check if the name already exists in Wikidata
    for (let row of nameRows) {
      const languageInput = row.querySelector('input[list]');
      const nameInput = row.querySelector('.name-input input[type="text"]');
      const sourceInput = row.querySelector('.source-input input[type="text"]');
      const aliasStatus = row.querySelector('.alias-status');

      const languageCode = languageInput.value;
      const selectedOption = row.querySelector(
        `option[value="${languageCode}"]`,
      );
      const languageLabel = selectedOption ? selectedOption.textContent : '';

      // get feedback elements for valid and invalid inputs respectively for language and name
      const languageFeedbackValid = row.querySelector(
        '.language-input .valid-feedback',
      );
      const languageFeedbackInvalid = row.querySelector(
        '.language-input .invalid-feedback',
      );
      const nameFeedbackValid = row.querySelector(
        '.name-input .valid-feedback',
      );
      const nameFeedbackInvalid = row.querySelector(
        '.name-input .invalid-feedback',
      );
      const sourceFeedbackInvalid = row.querySelector(
        '.source-input .invalid-feedback',
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

      // check if name is empty
      if (nameInput.value.trim() === '') {
        nameInput.classList.add('is-invalid');
        nameInput.classList.remove('is-valid');
        nameFeedbackInvalid.textContent =
          'Please enter a name for this instrument in the selected language.';
        allValid = false;
      } else {
        try {
        // Check if name is already an alias or label on Wikidata
        const result = await existOnWikidata(
          wikidataId,
          languageCode,
          languageLabel,
          nameInput.value,
        )
        if (result.exists) {
          nameInput.classList.remove('is-valid');
          nameInput.classList.add('is-invalid');
          nameFeedbackInvalid.textContent =
            `This instrument already has this name on Wikidata in ${languageLabel} (${languageCode}).`;
          allValid = false;
          continue; // Skip to the next row if the name already exists
        } else {
          nameInput.classList.add('is-valid');
          nameInput.classList.remove('is-invalid');
          languageInput.classList.add('is-valid');
          languageInput.classList.remove('is-invalid');
          nameFeedbackValid.textContent =
            'This instrument does not have this name listed on Wikidata yet ! You can add a new name.';
        }
        } catch (error) {
          displayMessage(
            'There was an error checking Wikidata. Please try again later.',
            'danger',
          );
          return; // Stop further processing
        }

        try {
          const result = await isAlias(
            wikidataId,
            languageCode,
            languageLabel,
          );

          // If language has a label, input is an Alias
          if (result.exists) {
            aliasStatus.value = "true";
          } else {
            aliasStatus.value = "false";
          } 
        } catch (error) {
          displayMessage(
            'There was an error checking Wikidata. Please try again later.',
            'danger',
          );
          return; // Stop further processing
        }
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

      console.log('Checking naming:', nameInput.value);

      

      // Add the result to the confirmation message
      publishResults += `<br />Language: ${languageLabel} (${languageCode})
      <br>Name: ${nameInput.value} 
      <br>Source: ${sourceInput.value}
      <br> The entry will be saved as an ${aliasStatus.value === "true" ? 'alias' : 'label'} on Wikidata.<br />`;
    
    }

    // If all rows are valid, show the confirmation modal
    if (allValid) {
      document.getElementById('publishResults').innerHTML =
        `You will publish the following:<br />${publishResults}`;
      const confirmationModal = new bootstrap.Modal(
        document.getElementById('confirmationModal'),
      );
      confirmationModal.show();
    }
  });

// the number of rows in the modal
let rowIndex = 1;

// Function to reset the modal and ensure only one row is present
function resetModal() {
  const nameRows = document.getElementById('nameRows');
  nameRows.innerHTML = ''; // Clear all rows
  nameRows.appendChild(createRow(1)); // Add initial row
  updateRemoveButtons(); // Ensure remove buttons are updated on reset
  rowIndex = 1; // Reset row index
}

// Add a new row when the 'Add another row' button is clicked
document.getElementById('addRowBtn').addEventListener('click', function () {
  rowIndex++;
  const nameRows = document.getElementById('nameRows');
  nameRows.appendChild(createRow(rowIndex));
  updateRemoveButtons(); // Update remove buttons after adding a new row
});

document.addEventListener('DOMContentLoaded', function () {
  const storedData = localStorage.getItem('addNameFormData');
  if (storedData) {
    // Show the modal
    const addNameModal = new bootstrap.Modal(
      document.getElementById('addNameModal'),
    );
    addNameModal.show();
    // Restore form data
    restoreFormData(storedData);
  } else {
    resetModal();
  }
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
      const aliasStatus = row.querySelector('.alias-status');
      // const descriptionInput = row.querySelector(
      //   '.description-input input[type="text"]',
      // );
      // const aliasInput = row.querySelector('.alias-input input[type="text"]');

      const languageCode = languageInput.value;
      const nameValue = nameInput.value;
      const sourceValue = sourceInput.value;
      const aliasValue = aliasStatus.value;
      // const descriptionValue = descriptionInput.value || '';
      // const aliasValue = aliasInput.value || '';

      entries.push({
        language: languageCode,
        name: nameValue,
        source: sourceValue,
        alias: aliasValue,
        // description: descriptionValue,
        // alias: aliasValue,
      });
    });

    // Get the CSRF token
    const csrftoken = document.querySelector(
      '[name=csrfmiddlewaretoken]',
    ).value;

    // Send the request to publish
    fetch(`/add-name/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({
        wikidata_id: wikidataId,
        entries: entries,
        // publish_to_wikidata: publishToWikidata,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          alert('Data published successfully!');
          // Close both modals
          const addNameModal = bootstrap.Modal.getInstance(
            document.getElementById('addNameModal'),
          );
          const confirmationModal = bootstrap.Modal.getInstance(
            document.getElementById('confirmationModal'),
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

      window.location.reload(); // Reload the page to reflect changes
  });

// Get the modal element
var deleteNameModal = document.getElementById('deleteNameModal');
let instrumentNameId = null; // Variable to store the instrument name ID

// Handle modal show event
deleteNameModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget;
  if (button != undefined) {
    var instrumentName = button.getAttribute('data-instrument-name');
    var instrumentSource = button.getAttribute(
      'data-instrument-source');
    instrumentNameId = button.getAttribute(
      'data-instrument-id');
    console.log('Instrument Name ID:', instrumentNameId);

    deleteNameModal.querySelector('#instrumentNameInModal').textContent =
      instrumentName;
    deleteNameModal.querySelector('#instrumentSourceInModal').textContent =
      instrumentSource;
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
        alert('Name deleted successfully!');
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