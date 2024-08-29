function displaySelectedImage(event, elementId) {
  const selectedImage = document.getElementById(elementId);
  const fileInput = event.target;

  if (fileInput.files && fileInput.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      selectedImage.src = e.target.result;
    };

    reader.readAsDataURL(fileInput.files[0]);
  }
}

// Get the modal element
var uploadImagesModal = document.getElementById('uploadImagesModal');

uploadImagesModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget;
  var instrumentName = button.getAttribute('data-instrument-name');
  var instrumentWikidataId = button.getAttribute('data-instrument-wikidata-id');
  var instrumentNameInModal = uploadImagesModal.querySelector(
    '#instrumentNameInModal'
  );
  instrumentNameInModal.textContent = instrumentName;

  var instrumentWikidataIdInModal = uploadImagesModal.querySelector(
    '#instrumentWikidataId'
  );
  instrumentWikidataIdInModal.textContent = instrumentWikidataId;
});

document
  .getElementById('imageFiles')
  .addEventListener('change', function (event) {
    var previewContainer = document.getElementById('previewImages');
    previewContainer.innerHTML = ''; // Clear existing previews

    var files = event.target.files;

    for (var i = 0; i < files.length; i++) {
      var file = files[i];

      // Ensure that the file is an image
      if (file.type.startsWith('image/')) {
        var reader = new FileReader();

        reader.onload = (function (file) {
          return function (e) {
            var colDiv = document.createElement('div');
            colDiv.className = 'col-3';

            var img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'img-thumbnail';
            img.alt = file.name;
            img.style.maxHeight = '150px';
            img.style.objectFit = 'cover';

            colDiv.appendChild(img);
            previewContainer.appendChild(colDiv);
          };
        })(file);

        reader.readAsDataURL(file);
      }
    }
  });
