// misc things to do on initial page load
document.addEventListener('DOMContentLoaded', function() {
    up.modal.config.history = false;
    console.clear();
});


// update google analytics when unpoly link is followed
up.on('up:link:follow ', function(event) {
    target_page = event.target.attributes.href.value;
    gtag('config', 'UA-176045696-1' , {'page_path': target_page});
});
