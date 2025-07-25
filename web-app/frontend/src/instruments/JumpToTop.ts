document.addEventListener('DOMContentLoaded', function () {
  const jumpToTopBtn = document.getElementById('jump-to-top');

  // Show/hide button based on scroll position
  function toggleJumpToTopBtn() {
    if (window.pageYOffset > 300) {
      jumpToTopBtn.classList.remove('d-none');
      jumpToTopBtn.classList.add('d-block');
    } else {
      jumpToTopBtn.classList.add('d-none');
      jumpToTopBtn.classList.remove('d-block');
    }
  }

  // Smooth scroll to top
  function scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  // Event listeners
  window.addEventListener('scroll', toggleJumpToTopBtn);
  jumpToTopBtn.addEventListener('click', scrollToTop);

  // Initial check
  toggleJumpToTopBtn();
});
