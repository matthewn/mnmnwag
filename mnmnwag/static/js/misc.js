/* eslint-disable no-undef */

// on initial page load...
document.addEventListener('DOMContentLoaded', function() {
    hljs.configure({useBR: true});

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

    console.clear();
});


// when any unpoly link is followed...
up.on('up:link:follow', function(event) {
    // update google analytics
    target_page = event.target.attributes.href.value;
    gtag('config', 'UA-176045696-1' , {'page_path': target_page});
});


// trigger highlight.js when needed
up.compiler('.blog-post code', function(element) {
    hljs.highlightBlock(element);
});
