// on initial page load...
document.addEventListener('DOMContentLoaded', function() {
    up.modal.config.history = false;
    hljs.configure({useBR: true});
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
})
