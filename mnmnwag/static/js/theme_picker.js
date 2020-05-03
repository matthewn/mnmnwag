// !!! depends on functions defined in cookies.js !!!

const body = document.getElementsByTagName('body')[0];
const links = '#theme-picker li a';
const prefix = 'theme-';


document.addEventListener('DOMContentLoaded', function() {
    [].forEach.call(document.querySelectorAll(links), function(link) {
        link.addEventListener('click', changeTheme);
    });
    if (getCookie('themeClass')) setTheme(getCookie('themeClass'));
    else markCurrentTheme();
});


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
