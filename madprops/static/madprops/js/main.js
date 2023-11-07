/* eslint-disable no-undef */

const backtotop = document.getElementById('backtotop');

function toggleBacktotopVisibility() {
    const scrollY = window.scrollY || window.pageYOffset;
    const elementTop = backtotop.offsetTop;

    if (scrollY > elementTop - (window.innerHeight / 2) + 200) {
        backtotop.classList.add('visible');
    } else {
        backtotop.classList.remove('visible');
    }
}

window.addEventListener('scroll', toggleBacktotopVisibility);

up.log.config.banner = false;
