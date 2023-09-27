function initMasonry() {
    var masonryGrid = document.getElementById('masonry-grid');

    var masonry = new Masonry(masonryGrid, {
        itemSelector: '.col',
        columnWidth: '.col',
        percentPosition: true,
    });
}

var masonryGrid = document.getElementById('masonry-grid');
imagesLoaded(masonryGrid, initMasonry);

window.addEventListener('resize', initMasonry);