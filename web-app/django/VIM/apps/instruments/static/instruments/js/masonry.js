// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Initialize Masonry
    var masonryGrid = document.getElementById("masonry-grid");
    var masonry = new Masonry(masonryGrid, {
        percentPosition: true, 
    });

    // Initialize ImagesLoaded
    var imgLoad = imagesLoaded(masonryGrid);

    // When all images are loaded, relayout Masonry
    imgLoad.on("always", function () {
        masonry.layout();
    });
});
