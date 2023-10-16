function googleTranslateElementInit() {
    new google.translate.TranslateElement({
    pageLanguage: 'en',
    layout: google.translate.TranslateElement.InlineLayout.HORIZONTAL
    }, 'google_translate_element');
    
    const googleSelect = document.getElementsByClassName("goog-te-combo")[0];
    googleSelect.classList.add('btn', 'p-0', 'm-0', 'h-100');

    const parent = googleSelect.parentElement;
    parent.classList.add('h-100', 'd-flex', 'align-items-center');

    const grandparent = parent.parentElement;
    grandparent.classList.add('h-100', 'd-flex', 'align-items-center');
} 