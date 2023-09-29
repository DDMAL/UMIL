
const masonryBtn = document.getElementById("masonry-btn");
const listBtn = document.getElementById("list-btn");
const stdBtn = document.getElementById("std-btn");

const masonryView = document.getElementById('masonry-view');
const listView = document.getElementById('list-view');
const stdView = document.getElementById('std-view');

masonryBtn.addEventListener("click", () => {
    masonryBtn.style.display = "none";
    listBtn.style.display = "";
    masonryView.style.display = "none";
    listView.style.display = "";
});


listBtn.addEventListener("click", () => {
    listBtn.style.display = "none";
    stdBtn.style.display = "";
    listView.style.display = "none";
    stdView.style.display = "";
});


stdBtn.addEventListener("click", () => {
    masonryBtn.style.display = "";
    stdBtn.style.display = "none";
    masonryView.style.display = "";
    stdView.style.display = "none";
});