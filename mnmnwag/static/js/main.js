/* eslint-disable no-undef */

document.addEventListener('swiped-left', function() {
    document.querySelector('#go-left').click();
});

document.addEventListener('swiped-right', function() {
    document.querySelector('#go-right').click();
});

document.addEventListener('DOMContentLoaded', function() {
    // console splash
    console.log('\nwe were talking\nabout the love that’s grown so cold\nand the people who gain the world and lose their soul\nthey don’t know\nthey can’t see\nare you one of them?\n\n— George Harrison\n\n');

    // fix firefox android edge case (theme missing on initial page load)
    if (getCookie('themeClass').length > 0) setTheme(getCookie('themeClass'));

    // if no theme chosen, but OS wants dark mode, give user the dark theme
    if ( (getCookie('themeClass') == '') && (window.matchMedia('(prefers-color-scheme: dark)').matches) ) {
        setTheme('theme-dark');
    }
});


//
// UNPOLY
//

up.layer.config.modal.history = false;
up.log.config.banner = false;

up.macro('[up-blog-link]', function(link) {
    link.setAttribute('up-target', '#content .blog');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

up.macro('[up-content-link]', function(link) {
    link.setAttribute('up-target', '#content');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

up.macro('[up-nav-link]', function(link) {
    link.setAttribute('up-target', '#navbar, #content');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

// when any unpoly link is followed...
up.on('up:link:follow', function(event) {
    // update google analytics
    target_page = event.target.attributes.href.value;
    gtag('config', 'UA-176045696-1' , {'page_path': target_page});
});


//
// HIGHLIGHT.JS
//

hljs.configure({useBR: true});

// trigger highlight.js when needed
up.compiler('.blog-post code', function(element) {
    hljs.highlightBlock(element);
});
