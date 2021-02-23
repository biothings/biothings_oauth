!(function() {
  const navbarNav = document.querySelector('.js-navbar-nav');
  const navbarTrigger = document.querySelector('.js-navbar-trigger');
  const navbarClose = document.querySelector('.js-navbar-close');
  const bodyOverlay = document.querySelector('.js-body-overlay');

  function showNavbar() {
    navbarNav.classList.add('is-open');
    bodyOverlay.classList.add('is-visible');
  }

  function hideNavbar() {
    navbarNav.classList.remove('is-open');
    bodyOverlay.classList.remove('is-visible');
  }

  navbarTrigger.addEventListener('click', showNavbar);
  navbarClose.addEventListener('click', hideNavbar); 
  bodyOverlay.addEventListener('click', hideNavbar);
}());