const paginationModal = document.getElementById("paginationModal");
const instrumentNumElement = document.getElementById('instrumentNum');
const instrumentNum = instrumentNumElement.getAttribute('data-instrument-num');

const savePaginationBtn = document.getElementById("save-pagination-setting");
const paginateByInput = document.getElementById("paginate-by");
const pageNumInput = document.getElementById("page-num");

updatePaginationSetting();

function setPaginationSetting(paginateBy, pageNum) {
    localStorage.setItem("paginate_by", paginateBy);
    localStorage.setItem("page", pageNum);
}

function getPaginationSetting() {
    return {
        paginate_by: localStorage.getItem("paginate_by"),
        page: localStorage.getItem("page")
    };
}

function updatePaginationSetting() {
    currentPaginateBy = getPaginationSetting().paginate_by || 20;
    currentPageNum = getPaginationSetting().page || 1;
    paginateByInput.value = currentPaginateBy;
    pageNumInput.value = currentPageNum;
}

savePaginationBtn.addEventListener("click", () => {
    const url = new URL(window.location.href);
    url.searchParams.set("paginate_by", paginateByInput.value);
    url.searchParams.set("page", pageNumInput.value);
    window.location.href = url.href;

    setPaginationSetting(paginateByInput.value, pageNumInput.value);
    updatePaginationSetting();
});