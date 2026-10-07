// DEPENDENCIES: ./cookies.js, ./vendor/unpoly.js

const links = '#theme-picker a';
const prefix = 'theme-';
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');


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


const changeTheme = function(event) {
    event.preventDefault();
    setTheme(prefix + this.getAttribute('data-theme'));
    up.cache.expire();
};


// the system theme also applies the light or dark class it resolves to
const setTheme = function(className) {
    const classes = document.body.classList;
    classes.remove(...[...classes].filter(c => c.startsWith(prefix)));
    classes.add(className);
    if (className === 'theme-system') classes.add(prefersDark.matches ? 'theme-dark' : 'theme-light');
    setCookie('themeClass', className);
};


prefersDark.addEventListener('change', function() {
    if (document.body.classList.contains('theme-system')) setTheme('theme-system');
});
