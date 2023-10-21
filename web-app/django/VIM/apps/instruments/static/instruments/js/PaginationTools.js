const instrumentNumElement = document.getElementById('instrumentNum');
const instrumentNum = instrumentNumElement.getAttribute('data-instrument-num');
const pageNumInput = document.getElementById("page-num");
const pageBtns = document.querySelectorAll(".page-link");
const optionRadios = document.querySelectorAll(".option-radio");

updatePaginationSetting();

function updatePaginationSetting() {
    const url = new URL(window.location.href);
    const page = url.searchParams.get("page") || 1;
    const paginateBy = url.searchParams.get("paginate_by") || 20;
    setPage(page);
    setPaginateBy(paginateBy);
    pageNumInput.max = Math.ceil(instrumentNum / paginateBy);
}

function setPaginateBy(paginateBy) {
    localStorage.setItem("paginate_by", paginateBy);
}

function setPage(pageNum) {
    localStorage.setItem("page", pageNum);
}

function getPaginateBy() {
    return localStorage.getItem("paginate_by");
}

function getPage() {
    return localStorage.getItem("page");
}

optionRadios.forEach(function(radio) {
    if (radio.id == getPaginateBy()) {
        radio.checked = true;   
    }
});

optionRadios.forEach(function(radio) {
    radio.addEventListener("change", function() {
        if (radio.checked) {
            const selectedOptionInt = parseInt(radio.id);
            setPaginateBy(selectedOptionInt);
            maxPageNum = Math.ceil(instrumentNum / getPaginateBy());
            validPageNum = Math.min(Math.max(getPage(), 1), maxPageNum);
            if (validPageNum !== getPage()) {
                setPage(validPageNum);
            }
            refreshPage();
        }
    });
});

pageNumInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        maxPageNum = Math.ceil(instrumentNum / getPaginateBy());
        validPageNum = Math.min(Math.max(pageNumInput.value, 1), maxPageNum);
        pageNumInput.value = validPageNum;
        pageNumInput.max = maxPageNum;
        setPage(validPageNum);
        refreshPage();
    }
});

pageBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        btn.href = btn.href + "&paginate_by=" + getPaginateBy();
    });
});

function refreshPage() {
    const url = new URL(window.location.href);
    url.searchParams.set("page", getPage());
    url.searchParams.set("paginate_by", getPaginateBy());
    window.location.href = url.href;
}