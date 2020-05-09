// !!! depends on functions defined in cookies.js !!!

const body = document.getElementsByTagName('body')[0];
const links = '#theme-picker li a';
const prefix = 'theme-';


// on page load, enable cookied theme (if it exists)
document.addEventListener('DOMContentLoaded', function() {
    if (getCookie('themeClass')) setTheme(getCookie('themeClass'));
    else markCurrentTheme();
});


// use unpoly to attach event listeners to theme picker links
// (both on page load & after subsequent AJAX calls)
up.compiler(links, function(link) {
    link.addEventListener('click', changeTheme);
})


const getTheme = function() {
    for (let className of body.classList.values()) {
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
    body.classList.remove(prefix + getTheme());
    body.classList.add(className);
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
