/* eslint-disable no-undef */

// DEPENDENCIES: vendor/unpoly.js
//
// style notes generated by wagtail-footnotes as inline annotations, inspired by
// https://www.viget.com/articles/of-note-better-text-annotations-for-the-web/


up.compiler('#footnotes', function(el) {
    processFootnotes(el);

    // if note specified in URL fragment identifier, open it
    frag = window.location.hash.slice(1);
    if (frag) {
        marker = document.getElementById(frag.replace('footnote', 'footnote-source'));
        if (marker) marker.querySelector('sup').click();
    }
});


function processFootnotes(el) {
    // given a <div id="footnotes"> (as generated by wagtail-footnotes),
    // gather up the footnotes, move them to their new positions, and slap an
    // event handler on the marker links
    let items = el.querySelectorAll('li');
    let ids = [];

    for (let li of items) {
        if (li.id) ids.push(li.id);
    }

    for (let id of ids) {
        let footnote = document.getElementById(id);
        let link_id = id.replace('-', '-source-');

        let annotation = document.createElement('span');
        annotation.setAttribute('id', id);
        annotation.className = 'annotation';

        let paragraphs = footnote.querySelectorAll('p');
        paragraphs.forEach((paragraph) => {
            let graf = paragraph.cloneNode(true);
            annotation.appendChild(graf);
        });

        let link = document.getElementById(link_id);
        link.insertAdjacentElement('afterend', annotation);

        let span = document.createElement('span');
        span.textContent = '🞬 hide note';

        link.setAttribute('aria-label', 'Show note');
        link.setAttribute('title', 'show note');
        link.classList.add('annotation-toggle');
        link.appendChild(document.createTextNode(' '));
        link.appendChild(span);
        link.addEventListener('click', toggleAnnotation);
    }

    el.remove();
}


function toggleAnnotation(ev) {
    // event handler for the annotation marker links
    // toggles display of the annotation
    ev.preventDefault();
    let link;
    if (ev.target.tagName === 'A') {
        link = ev.target;  // target was hit with keyboard Enter
    } else {
        link = ev.target.parentNode;  // target was hit with mouse
    }
    let ann = link.nextElementSibling;
    let sup = link.querySelector('sup');
    let span = link.querySelector('span');

    if (ann.classList.contains('expanded')) {  // CLOSE

        sup.style.display = 'inline';
        span.style.display = 'none';
        link.setAttribute('aria-label', 'show note');
        link.setAttribute('title', 'show note');
        ann.classList.remove('expanded');
        setTimeout(() => { ann.classList.remove('displayed'); }, 300);

    } else {  // OPEN

        sup.style.display = 'none';
        span.style.display = 'inline';
        link.setAttribute('aria-label', 'hide note');
        link.removeAttribute('title');
        ann.classList.add('displayed');
        setTimeout(() => { ann.classList.add('expanded'); }, 300);

    }
}
