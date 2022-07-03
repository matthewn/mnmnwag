/* eslint-disable no-undef */

// DEPENDENCIES: ./cookies.js, ./theme_picker.js, ../vendor/unpoly.js

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

// hook up swipe events, courtesy of swiped-events.js
document.addEventListener('swiped-left', function() {
    document.querySelector('#go-next').click();
});
document.addEventListener('swiped-right', function() {
    document.querySelector('#go-prev').click();
});


//
// UNPOLY
//

up.layer.config.modal.history = false;
up.log.config.banner = false;

// up-blog-link refreshes mainbar in /blog section
up.macro('[up-blog-link]', function(link) {
    link.setAttribute('up-target', '#content .blog, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

// up-content-link refreshes entire content section
up.macro('[up-content-link]', function(link) {
    link.setAttribute('up-target', '#content, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
    link.setAttribute('up-scroll', '#header');
});

// up-content-link w/o a scroll to top -- used on comment links
up.macro('[up-content-link-notop]', function(link) {
    link.setAttribute('up-target', '#content, .wagtail-userbar-items');
    link.setAttribute('up-transition', 'cross-fade');
});

// up-nav-link refreshes entire content section + navbar
up.macro('[up-nav-link]', function(link) {
    link.setAttribute('up-target', '#navbar, #content, .wagtail-userbar-items');
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

// handle twitter embeds
up.on('up:fragment:inserted', function(event, fragment) {
    if (fragment.innerHTML.includes('twitter-tweet')) {
        if (typeof twttr === 'undefined') {
            // https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/set-up-twitter-for-websites
            window.twttr = (function(d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0], t = window.twttr || {};
                if (d.getElementById(id)) return t;
                js = d.createElement(s);
                js.id = id;
                js.src = 'https://platform.twitter.com/widgets.js';
                fjs.parentNode.insertBefore(js, fjs);
                t._e = [];
                t.ready = function(f) {
                    t._e.push(f);
                };
                return t;
            }(document, 'script', 'twitter-wjs'));
        }
        twttr.ready(
            function () {
                return window.twttr.widgets.load();
            }
        );
    }
});


//
// HIGHLIGHT.JS
//

hljs.configure({useBR: true});

// trigger highlight.js when needed
up.compiler('.blog-post code', function(element) {
    hljs.highlightBlock(element);
});
