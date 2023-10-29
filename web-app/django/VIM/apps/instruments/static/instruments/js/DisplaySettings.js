const masonryBtn = document.getElementById("masonry-btn");
const stdBtn = document.getElementById("std-btn");

const masonryView = document.getElementById('masonry-view');
const stdView = document.getElementById('std-view');

updateDisplayMode();

function setDisplayMode(displayMode) {
    localStorage.setItem('displayMode', displayMode);
}

function getDisplayMode() {
    return localStorage.getItem('displayMode');
}

function updateDisplayMode() {
    const currentDisplayMode = getDisplayMode() || 'masonry'; 
    switch (currentDisplayMode) {
        case 'masonry':
            setMasonryView();
            masonryView.style.display = "";
            stdView.style.display = "none";
            masonryBtn.classList.toggle("highlighted-btn");
            stdBtn.classList.remove("highlighted-btn");
            break;
        case 'standard':
            masonryView.style.display = "none";
            stdView.style.display = "";
            stdBtn.classList.toggle("highlighted-btn");
            masonryBtn.classList.remove("highlighted-btn");
            break;
        default:
            break;
    }
}

// Switch to the next mode
masonryBtn.addEventListener("click", () => {
    if (getDisplayMode() !== 'masonry') {
        setDisplayMode('masonry');
        updateDisplayMode();
    }
});

stdBtn.addEventListener("click", () => {
    if (getDisplayMode() !== 'standard') {
        setDisplayMode('standard');
        updateDisplayMode();
    }
});


function setMasonryView() {
    // Initialize Masonry
    var masonryGrid = document.getElementById("masonry-view");
    var masonry = new Masonry(masonryGrid, {
        percentPosition: true, 
    });

    // Initialize ImagesLoaded
    var imgLoad = imagesLoaded(masonryGrid);

    // When all images are loaded, relayout Masonry
    imgLoad.on("always", function () {
        masonry.layout();
    });
}

// Instrument badge settings
const instrumentLanguage = document.querySelector("#instrument-language-element");
const instrumentBadge = document.querySelector("#instrument-language-badge");

updateInstrumentBadge();

function updateInstrumentBadge() {
    const hideInstrumentBadge = localStorage.getItem('hideInstrumentBadge') || false;
    if (hideInstrumentBadge) {
        instrumentBadge.style.display = "none";
    } else {
        instrumentBadge.style.display = "";
    }
}

instrumentLanguage.addEventListener("click", function () {
    localStorage.setItem("hideInstrumentBadge", true);
    updateInstrumentBadge();
});


// HBS facet settings
const items = document.querySelectorAll('.list-group-item');

updateHbsFacet();

function updateHbsFacet() {
    const url = new URL(window.location.href);
    const selectedHbsFacet = url.searchParams.get("hbs_facet") || '';
    localStorage.setItem('selectedHbsFacet', selectedHbsFacet);
    items.forEach(item => {
        current_item = item.getAttribute('current-value');
        if (current_item === selectedHbsFacet) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });
}

items.forEach(item => {
    item.addEventListener('click', function () {
        current_item = item.getAttribute('current-value');
        localStorage.setItem('selectedHbsFacet', current_item);
        updateHbsFacet();
    });
});

