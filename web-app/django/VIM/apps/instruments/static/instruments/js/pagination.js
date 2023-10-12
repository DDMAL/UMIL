const paginationModal = document.getElementById("paginationModal");
const instrumentNumElement = document.getElementById('instrumentNum');
const instrumentNum = instrumentNumElement.getAttribute('data-instrument-num');

const savePaginationBtn = document.getElementById("save-pagination-setting");
const paginateByInput = document.getElementById("pagination-range");
const pageNumInput = document.getElementById("page-num");
const rangeValue = document.getElementById("range-value");

const pageBtns = document.querySelectorAll(".page-link");

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

function pageNumInputValidation() {
    maxPageNum = Math.ceil(instrumentNum / paginateByInput.value);
    if (pageNumInput.value < 1) {
        pageNumInput.value = 1;
    } else if (pageNumInput.value > maxPageNum) {
        pageNumInput.value = maxPageNum;
    }
}

paginateByInput.addEventListener("input", function () {
    rangeValue.textContent = this.value;
    maxPageNum = Math.ceil(instrumentNum / this.value);
    if (pageNumInput.value > maxPageNum) {
        pageNumInput.value = maxPageNum;
    }
    pageNumInput.max = maxPageNum;
});

savePaginationBtn.addEventListener("click", () => {
    pageNumInputValidation();
    const url = new URL(window.location.href);
    url.searchParams.set("paginate_by", paginateByInput.value);
    url.searchParams.set("page", pageNumInput.value);
    window.location.href = url.href;
    setPaginationSetting(paginateByInput.value, pageNumInput.value);
    updatePaginationSetting();
});

pageBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        paginate_by = localStorage.getItem("paginate_by");
        btn.href = btn.href + "&paginate_by=" + paginate_by;
    });
});