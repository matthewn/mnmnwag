/* eslint-disable no-undef */

document.addEventListener('DOMContentLoaded', function() {
    document.body.classList.remove('nojs');
});

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

//
// UNPOLY
//

up.log.config.banner = false;

// up-nav-link refreshes entire content section + navbar
up.macro('[up-nav-link]', function(link) {
    link.setAttribute('up-target', '#navbar, #content, #wagtail-unpoly');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

// up-content-link refreshes entire content section
up.macro('[up-content-link]', function(link) {
    link.setAttribute('up-target', '#content, #wagtail-unpoly');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

// when any unpoly link is followed...
up.on('up:link:follow', function(event) {
    // ping goatcounter
    window.goatcounter.count({
        path: event.target.attributes.href.value,
        title: '',
    });
});
