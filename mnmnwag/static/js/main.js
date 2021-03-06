/* eslint-disable no-undef */

document.addEventListener('DOMContentLoaded', function() {
    // console splash
    console.clear();
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

up.modal.config.history = false;

up.macro('[up-blog-link]', function(link) {
    link.setAttribute('up-target', '#header, #content .blog, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
});

up.macro('[up-content-link]', function(link) {
    link.setAttribute('up-target', '#header, #content, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
});

up.macro('[up-nav-link]', function(link) {
    link.setAttribute('up-target', '#header, #navbar, #content, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
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
