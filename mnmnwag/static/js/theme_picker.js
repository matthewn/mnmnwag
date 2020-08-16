// DEPENDENCIES: ./cookies.js, ../vendor/unpoly.js

const body = function() { return document.getElementsByTagName('body')[0]; };
const picker = '#theme-picker';
const links = '#theme-picker li a';
const prefix = 'theme-';


// on return to page via back button, enable cookied theme (if it exists)
//
// NOTE TO SELF: up:history:restored is marked as 'experimental' --
// this bit could thus require refactoring at some point in the future
up.on('up:history:restored', function() {
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
    let className = prefix + this.textContent.toLowerCase();
    setTheme(className);
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
