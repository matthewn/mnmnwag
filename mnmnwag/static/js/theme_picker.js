/* eslint-disable no-undef */

// DEPENDENCIES: ./cookies.js, ../vendor/unpoly.js

const body = function() { return document.getElementsByTagName('body')[0]; };
const picker = '#theme-picker';
const links = '#theme-picker a';
const prefix = 'theme-';


// on return to page via back button, enable cookied theme (if it exists)
up.on('up:location:changed', function() {
    if (getCookie('themeClass').length > 0) setTheme(getCookie('themeClass'));
});


// use unpoly to attach event listeners to theme picker links
// (both on initial page load (if links are there) & after subsequent AJAX calls)
up.compiler(links, function(link) {
    link.addEventListener('click', changeTheme);
});


// use unpoly to call markCurrentTheme()
// (both on initial page load & after subsequent AJAX calls)
up.compiler(picker, function() {
    markCurrentTheme();
});


const getTheme = function() {
    for (let className of body().classList.values()) {
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
    body().classList.remove(prefix + getTheme());
    body().classList.add(className);
    setCookie('themeClass', className);
    markCurrentTheme();
};


const markCurrentTheme = function() {
    let currentTheme = getTheme();
    [].forEach.call(document.querySelectorAll(links), function(link) {
        if (link.textContent.toLowerCase() === currentTheme) {
            link.classList.add('current');
        } else {
            link.classList.remove('current');
        }
    });
};


// on page load, if no theme cookie, switch to dark mode if preferred
document.addEventListener('DOMContentLoaded', function() {
    if (getCookie('themeClass') === '') {
        const prefersDarkTheme = window.matchMedia('(prefers-color-scheme: dark)');
        if (prefersDarkTheme.matches) { setTheme('theme-dark'); }
    }
});
