
const masonryBtn = document.getElementById("masonry-btn");
const listBtn = document.getElementById("list-btn");
const stdBtn = document.getElementById("std-btn");


masonryBtn.addEventListener("click", () => {
    masonryBtn.style.display = "none";
    listBtn.style.display = "";
    stdBtn.style.display = "none";
});


listBtn.addEventListener("click", () => {
    masonryBtn.style.display = "none";
    listBtn.style.display = "none";
    stdBtn.style.display = "";
});


stdBtn.addEventListener("click", () => {
    masonryBtn.style.display = "";
    listBtn.style.display = "none";
    stdBtn.style.display = "none";
});
