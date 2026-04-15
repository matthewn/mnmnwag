// DEPENDENCIES: ./cookies.js, ../vendor/unpoly.js

const links = '#theme-picker a';
const prefix = 'theme-';


// on return to page via back button, enable cookied theme (if it exists)
up.on('up:location:changed', function() {
    const cookied = getCookie('themeClass');
    if (cookied.length > 0) setTheme(cookied);
});


// use unpoly to attach event listeners to theme picker links
// (both on initial page load (if links are there) & after subsequent AJAX calls)
up.compiler(links, function(link) {
    link.addEventListener('click', changeTheme);
});


const getTheme = function() {
    for (let className of document.body.classList.values()) {
        if (className.startsWith(prefix))
            return className.replace(prefix, '');
    }
};


const changeTheme = function(event) {
    event.preventDefault();
    let className = prefix + this.getAttribute('data-theme');
    setTheme(className);
    up.cache.expire();
};


const setTheme = function(className) {
    const current = getTheme();
    if (current) document.body.classList.remove(prefix + current);
    document.body.classList.add(className);
    setCookie('themeClass', className);
};


// on page load, if no theme cookie, switch to dark mode if preferred
document.addEventListener('DOMContentLoaded', function() {
    if (getCookie('themeClass') === '') {
        const prefersDarkTheme = window.matchMedia('(prefers-color-scheme: dark)');
        if (prefersDarkTheme.matches) { setTheme('theme-dark'); }
    }
});
