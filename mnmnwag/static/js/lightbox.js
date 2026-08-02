// DEPENDENCIES: ./vendor/unpoly.js
//
// The slide lightbox. Three slides are in the DOM at once -- prev, current,
// next -- laid side by side in a scroll-snap track, so a swipe is an ordinary
// scroll: the browser pans the image under the finger, carries the momentum and
// snaps, all on the compositor. We note where the track came to rest and ask
// Unpoly for the slide that landed, which returns a fresh three-up window
// centered on it. Because the panel we settle on holds the same image the new
// window will center -- already fetched, already decoded -- re-centering
// after the swap is invisible.

const SLIDESHOW_MS = 6000;
const SETTLE_MS = 120;  // fallback debounce where 'scrollend' is unsupported
const SCRIM_STEP_PX = 8;  // px granularity when sizing a caption scrim to its text
const JUMP_MS = 90;  // how long to keep gathering presses before jumping
const ADVANCE_MS = 700;  // how long a slideshow step waits on the scroll to land
const CLOSE_SWIPE_PX = 100;  // how far up or down a swipe must travel to close
const CLOSE_SWIPE_RATIO = 1.5;  // and how much more vertical than sideways it must be
const DRAG_START_PX = 12;  // slop before a touch counts as a dismissal drag
const DRAG_FULL_PX = 400;  // drag length at which the photo reaches its smallest and faintest
const SLIDE_DRAG_PX = 60;  // how far sideways a mouse drag must travel to change slides
const FLING_MS = 180;  // how long the photo takes to leave once a dismissal is settled
const SLIDESHOW_LABELS = { off: 'Start slideshow', on: 'Stop slideshow' };
const FULLSCREEN_LABELS = { off: 'Enter fullscreen', on: 'Exit fullscreen' };
const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)');

// Clicking outside all of these closes. Anchors and buttons are matched
// wholesale rather than by name, so a control added later is not a trapdoor.
const KEEPS_OPEN = 'img, a, button, figcaption';

// These outlive the fragment they were set from: every slide change replaces the
// lightbox and re-runs the compiler, so none of them can live inside it.
let slideshowOn = false;
let jumpTo = null;  // absolute slide position we mean to end up on
let jumpTimer = null;
let jumping = false;  // a jump is in flight; the track must not also navigate

// Width of each rendered line of text. getClientRects() yields a rect per box rather
// than per line — inline markup such as a link splits a line into several — so the rects
// sharing a line are unioned back together.
function lineWidths(el) {
    const range = document.createRange();
    range.selectNodeContents(el);

    const lines = new Map();
    for (const rect of range.getClientRects()) {
        if (!rect.width) continue;
        const key = Math.round(rect.top);
        const line = lines.get(key) ?? { left: Infinity, right: -Infinity };
        line.left = Math.min(line.left, rect.left);
        line.right = Math.max(line.right, rect.right);
        lines.set(key, line);
    }
    return [...lines.values()].map(({ left, right }) => right - left);
}

// A wrapped inline-block takes the full width available, not the width of the longest
// line it ended up with, which leaves dead scrim either side of centered text. Pin the box
// to that longest line instead — measuring the balanced wrap, then freezing it, because
// balance spreads the text to fill whatever width it is given: it would answer every
// narrowing with fresh slack, and no width would ever be narrow enough to settle on.
// A pinned box can still rewrap onto an extra line, so ease back out until it does not.
function fitScrim(caption) {
    for (const box of caption.children) {
        const asAuthored = () => {
            box.style.width = '';
            box.style.removeProperty('text-wrap');
        };

        asAuthored();
        const lines = lineWidths(box);
        if (lines.length < 2) continue;  // a single line already hugs its text

        const natural = box.getBoundingClientRect().width;
        const widest = Math.ceil(Math.max(...lines));
        box.style.setProperty('text-wrap', 'normal');  // hold the wrap just measured

        const holds = (width) => {
            box.style.width = `${width}px`;
            return lineWidths(box).length <= lines.length;
        };

        const candidates = Array.from(
            { length: Math.ceil((natural - widest) / SCRIM_STEP_PX) },
            (_, i) => widest + i * SCRIM_STEP_PX,
        );
        if (!candidates.some(holds)) asAuthored();  // nothing narrower held, so leave it be
    }
}

function setToggle(button, on, labels) {
    if (!button) return;
    button.classList.toggle('is-on', on);
    const text = on ? labels.on : labels.off;
    button.title = text;
    button.setAttribute('aria-label', text);  // icon-only buttons need a name
}

// Hand the neighbors their sources -- they ship inert so a nojs visitor, who is
// shown a plain image instead, never pays for them -- and mark any panel whose
// image has yet to arrive so it can show a spinner. The neighbors get one too, so
// a swipe onto one that has not arrived scrolls a spinner into view rather than a
// black panel. Returns nothing; wiring the load handlers is left to the caller.
function loadPanel(panel, listen) {
    const img = panel.querySelector('img');
    if (img.dataset.src) {
        img.srcset = img.dataset.srcset;
        img.src = img.dataset.src;
    }
    if (img.complete) return;

    const spinner = panel.querySelector('.lightbox-spinner');
    panel.classList.add('is-loading');
    spinner.hidden = false;
    const done = () => {
        panel.classList.remove('is-loading');
        spinner.hidden = true;
    };
    listen(img, 'load', done);
    listen(img, 'error', done);
}


// up.compiler from here to EOF; contents:
//
//   VARS       -- what the markup gave us, and the state that tracks it
//   TRACK      -- geometry: where the panels are and how we scroll to one
//   CHROME     -- pushing current state out into the controls
//   NAVIGATION -- settling, stepping, and jumps that outlive a swap
//   SLIDESHOW  -- the timed walk from one slide to the next
//   DISMISSAL  -- closing, and the drags that lead to it
//   CAPTIONS   -- scrim fitting, and the resize that invalidates it
//   WIRING     -- every addEventListener, grouped by input device
//   STARTUP    -- everything this fragment does the moment it appears
//   DESTRUCTOR
//
up.compiler('[up-lightbox]', (lightbox) => {

    // *** VARS ***********************************************************
    // Elements and numbers from the markup, then the per-slide state. (The
    // slideshow and jump state is module-level: it has to survive the swap.)

    const track = lightbox.querySelector('[up-lightbox-track]');
    const panels = [...lightbox.querySelectorAll('.lightbox-panel')];
    const captions = [...lightbox.querySelectorAll('.lightbox-panel figcaption')];
    const counter = lightbox.querySelector('[up-lightbox-counter]');
    const download = lightbox.querySelector('[up-lightbox-download]');
    const closeButton = lightbox.querySelector('.lightbox-close');
    const fullscreenButton = lightbox.querySelector('[up-lightbox-fullscreen]');
    const slideshowButton = lightbox.querySelector('[up-lightbox-slideshow]');
    const prevLink = lightbox.querySelector('[up-lightbox-prev]');
    const nextLink = lightbox.querySelector('[up-lightbox-next]');
    const jumpLink = lightbox.querySelector('.lightbox-jump');

    const index = Number(lightbox.dataset.currentIndex);  // which panel of the three
    const pos = Number(lightbox.dataset.pos);  // where that is in the whole block
    const total = Number(lightbox.dataset.total);
    const urlTemplate = lightbox.dataset.urlTemplate;

    let timer = null;  // the slideshow's wait on this slide
    let advanceFallback = null;  // sends us on if the scroll never lands
    let debounce = null;  // settle detection where 'scrollend' is missing
    let swipe = null;  // where a touch that might be a dismissal started
    let dragging = false;  // that touch has committed to a dismissal drag
    let grab = null;  // a mouse drag on the photo, once one is under way
    let grabbed = false;  // one just ended, so the click it produced is not a click
    let closing = false;  // the lightbox is on its way out; the track no longer votes


    // *** TRACK **********************************************************
    // Where the panels sit, and the one way anything moves between them.
    // Arrows, keys and the slideshow all scroll the track instead of following
    // their link, so every route between slides runs through the same snap --
    // and gets the same animation -- as a swipe does.

    // Assigning scrollLeft skips any smooth behavior, and settling back onto the
    // panel we are already on is a no-op in settled(), so re-centering cannot be
    // mistaken for a swipe.

    const recenter = () => { track.scrollLeft = panels[index].offsetLeft; };

    const nearest = () => {
        const gaps = panels.map((panel) => Math.abs(panel.offsetLeft - track.scrollLeft));
        return gaps.indexOf(Math.min(...gaps));
    };

    const moving = () => Math.abs(track.scrollLeft - panels[index].offsetLeft) > 1;

    const goTo = (target) => {
        if (target < 0 || target >= panels.length) return false;
        track.scrollTo({
            left: panels[target].offsetLeft,
            behavior: REDUCED_MOTION.matches ? 'auto' : 'smooth',
        });
        return true;
    };


    // *** CHROME *********************************************************
    // Pushing current state out into the controls: the counter and the download
    // link, which name whichever slide the viewer is looking at -- or,
    // mid-keypress, the one they are heading for -- and the fullscreen toggle.

    // Chrome follows the drag rather than waiting for the slide to land, so the
    // count and the download target belong to whatever is on screen.
    const syncChrome = () => {
        // showTarget is displaying a keypress destination; leave it alone
        if (jumpTo !== null) return;
        const panel = panels[nearest()];
        if (counter) counter.textContent = panel.dataset.counter;  // absent for a lone image
        download.href = panel.dataset.download;
    };

    // A keypress knows where it is going, so say so now rather than a scroll or a
    // fetch later. The arriving fragment carries the authoritative values.
    const showTarget = (target) => {
        if (counter) counter.textContent = `${target + 1} / ${total}`;
        const panel = panels.find((p) => Number(p.dataset.pos) === target);
        if (panel) download.href = panel.dataset.download;
    };

    // Fullscreen is owned by the document rather than by any one lightbox, so the
    // button is caught up to it on arrival as well as on every change.
    const syncFullscreen = () => {
        setToggle(fullscreenButton, Boolean(document.fullscreenElement), FULLSCREEN_LABELS);
    };


    // *** NAVIGATION *****************************************************
    // Two routes out of this fragment. A neighbor is reached by scrolling: the
    // track settles on it and settled() follows the corresponding link. Anywhere
    // further is outside the three-up window, so it is banked as a jump and
    // followed by URL -- and a jump, unlike a scroll, has to survive the swap it
    // causes, which is why its state lives at module scope.

    const settled = () => {
        // A dismissal owns the gesture outright. Firefox Mobile axis-locks loosely,
        // so a swipe meant as "close this" can drift the track far enough to look
        // like a swipe to the next slide -- which would navigate mid-dismissal.
        // We avoid that problem with the first line here.
        if (dragging || closing) return;
        if (grab?.axis) return;  // a mouse drag is still panning the track
        track.classList.remove('is-unsnapped');  // which it had turned snapping off for
        if (jumpTimer || jumping) return;  // a jump owns the navigation
        const landed = nearest();
        if (landed === index) return;  // includes the centering at startup
        const link = landed < index ? prevLink : nextLink;
        if (!link) return;
        clearTimeout(advanceFallback);  // the scroll landed; no rescue needed
        up.follow(link);
    };

    // Drop any destination banked from earlier presses, along with the timer that
    // was going to act on it.
    const forgetJump = () => {
        clearTimeout(jumpTimer);
        jumpTimer = null;
        jumpTo = null;
    };

    const runJump = () => {
        jumpTimer = null;
        // declining leaves jumpTo banked on purpose: a scroll already under way
        // can still carry us off, and the resume at startup is what brings us back
        if (jumpTo === null || jumpTo === pos || !jumpLink || !urlTemplate) return;
        if (!lightbox.isConnected) return;  // a later fragment owns the jump now
        jumping = true;
        jumpLink.setAttribute('href', urlTemplate.replace('{pos}', jumpTo));
        up.follow(jumpLink);
    };

    const banked = () => (jumpTo === null ? pos : jumpTo);

    // A neighbor from rest rides the track, so a key press gets a swipe's
    // animation. Anywhere else is outside the three-up window, so bank it and
    // let the presses accumulate: twelve taps means one navigation twelve slides
    // over, not twelve navigations.
    const goToPos = (wanted) => {
        const target = Math.max(0, Math.min(total - 1, wanted));
        if (target === banked()) return false;
        jumpTo = target;
        showTarget(target);

        const offset = target - pos;
        if (!jumpTimer && !jumping && !moving() && Math.abs(offset) === 1) {
            return goTo(index + offset);
        }

        clearTimeout(jumpTimer);
        jumpTimer = setTimeout(runJump, JUMP_MS);
        return true;
    };

    const step = (direction) => goToPos(banked() + direction);


    // *** SLIDESHOW ******************************************************
    // Each slide schedules only its own advance. Landing on the next slide
    // replaces this fragment and runs the compiler again, which schedules the
    // one after -- so the show walks the block a slide at a time, and simply
    // stops when it reaches a slide with nowhere further to go.

    const stopSlideshow = () => {
        clearTimeout(timer);
        clearTimeout(advanceFallback);
        slideshowOn = false;
        setToggle(slideshowButton, false, SLIDESHOW_LABELS);
    };

    // Advance by scrolling, so a slideshow step gets the same motion as a swipe.
    // But do not depend on it: scrolling only navigates by way of the track
    // settling, and if that does not happen -- a browser withholding scrollend,
    // a fragment measured before it has been laid out, a scroll that had nowhere
    // to go -- the wait is spent and nothing reschedules, which wedges the show
    // on the slide it reached. Follow the link outright when the scroll has not
    // carried us within ADVANCE_MS.
    const advance = () => {
        // scheduleAdvance only arms the timer when there is a next slide, so
        // this cannot fire. Kept anyway: the last thing to go wrong here left
        // the show wedged with no way to restart it, and stopping honestly is
        // the one outcome that stays recoverable.
        if (!nextLink) return stopSlideshow();

        goTo(index + 1);  // a next link means a next panel, so this always moves
        advanceFallback = setTimeout(() => up.follow(nextLink), ADVANCE_MS);
    };

    const scheduleAdvance = () => {
        clearTimeout(timer);
        if (!nextLink) return stopSlideshow();
        timer = setTimeout(advance, SLIDESHOW_MS);
    };


    // *** DISMISSAL ******************************************************
    // Closing, and the drag that leads to it. The photo tracks the drag,
    // shrinking and fading as it travels, so a half-hearted swipe shows what it
    // was about to do before springing back; past the threshold it keeps going
    // and leaves by the edge it was headed for. Touch and mouse both end up in
    // endVerticalDrag().

    // A slide reached by its own URL has no overlay to dismiss, so leaving means
    // a full load; replace() so we don't create a history entry.
    const closeLightbox = () => {
        closing = true;
        if (up.layer.isRoot()) window.location.replace(closeButton.href);
        else up.layer.dismiss();
    };

    // The tint is the lightbox's own background on the root layer and the modal's
    // backdrop in an overlay; either way it reads --lightbox-fade off this element.
    const backdrop = up.layer.isRoot() ? lightbox : up.layer.element;

    const fadeBackdrop = (fade, ms) => {
        backdrop.style.setProperty('--lightbox-fade', fade);
        backdrop.style.setProperty('--lightbox-fade-ms', `${ms}ms`);
    };

    // The tint lifts with the photo, letting the page underneath show through.
    const dragPanel = (panel, dy) => {
        const progress = Math.min(Math.abs(dy) / DRAG_FULL_PX, 1);
        panel.style.transition = '';
        panel.style.transform = `translateY(${dy}px) scale(${1 - progress * 0.25})`;
        panel.style.opacity = 1 - progress * 0.5;
        fadeBackdrop(1 - progress * 0.7, 0);  // no transition: it is tracking a finger
    };

    const releasePanel = (panel) => {
        panel.style.transition = REDUCED_MOTION.matches ? '' : 'transform 200ms, opacity 200ms';
        panel.style.transform = '';
        panel.style.opacity = '';
        fadeBackdrop(1, REDUCED_MOTION.matches ? 0 : 200);
    };

    const flingPanel = (panel, direction) => {
        if (REDUCED_MOTION.matches) return closeLightbox();
        closing = true;  // before the animation, not after it
        lightbox.style.pointerEvents = 'none';  // nothing to do but watch it leave

        // The neighbors have no part in a dismissal. Left in place they are still
        // subject to the track being relaid out and re-snapped as the panel
        // transforms and the overlay dismisses, which is what flashes a sliver of
        // one along an edge.
        panels.forEach((other) => { if (other !== panel) other.style.visibility = 'hidden'; });
        track.classList.add('is-unsnapped');

        fadeBackdrop(0, FLING_MS);
        panel.style.transition = `transform ${FLING_MS}ms ease-in, opacity ${FLING_MS}ms ease-in`;
        panel.style.transform = `translateY(${direction * window.innerHeight}px) scale(.5)`;
        panel.style.opacity = 0;
        setTimeout(closeLightbox, FLING_MS);
    };

    // Where every dismissal drag ends up, by touch or by mouse: far enough and the
    // photo leaves the way it was headed, short of it and it springs back.
    const endVerticalDrag = (panel, traveled) => {
        if (Math.abs(traveled) >= CLOSE_SWIPE_PX) flingPanel(panel, Math.sign(traveled));
        else releasePanel(panel);
    };


    // *** CAPTIONS *******************************************************
    // Every panel carries its own caption, so each one needs its scrim fitted --
    // dragging brings a neighbor's caption in with it. fitScrim measures and
    // remeasures, so keep it off the scroll path.

    const fitAll = () => {
        // callers outlive the destructor -- a frame, a resize frame, or however
        // long the fonts take -- so none of them is the destructor's to cancel
        if (!lightbox.isConnected) return;
        captions.forEach(fitScrim);
    };

    // A resize moves every panel, so re-center or the track is left nearest a
    // neighbor and settled() reads that as a swipe. Again after the frame,
    // because a rotating phone lays out more than once.
    //
    // fitScrim forces a layout per candidate width, so it waits for the frame
    // rather than running on every event of a resize drag.
    let framePending = false;
    const onResize = () => {
        recenter();
        if (framePending) return;
        framePending = true;
        requestAnimationFrame(() => {
            framePending = false;
            recenter();
            fitAll();
        });
    };


    // *** WIRING *********************************************************
    // Nothing below decides anything; each handler routes an input to one of the
    // operations above. Grouped by where the input comes from: the layer, the
    // track (scroll, then mouse drag, then touch), the window, and the controls.

    // Every listener files its own removal as it is registered, so the teardown
    // in the destructor cannot drift out of step with what was actually bound.
    const cleanups = [];
    const listen = (target, type, handler, options) => {
        target.addEventListener(type, handler, options);
        // capture is the only option removeEventListener matches on, so it is the
        // only one that has to be repeated here
        cleanups.push(() => target.removeEventListener(type, handler, options));
    };

    // *** Layer ***
    // Closing for good, which the destructor cannot tell from a slide change --
    // and the shared state has to survive one but not the other, or the next
    // lightbox opened resumes a slideshow or walks off to a stale slide.
    // Dismiss and not dismissed: by then Unpoly has pushed the location it saved
    // at open, a push it skips once we stand on that location ourselves.
    listen(document, 'up:layer:dismiss', (event) => {
        if (!event.layer.contains(lightbox)) return;
        up.history.replace(closeButton.href);
        forgetJump();
        stopSlideshow();
    });

    // *** Track: scrolling ***
    listen(track, 'scroll', syncChrome, { passive: true });

    // 'scrollend' is the honest signal; debounce where it is not available.
    if ('onscrollend' in window) {
        listen(track, 'scrollend', settled);
    } else {
        listen(track, 'scroll', () => {
            clearTimeout(debounce);
            debounce = setTimeout(settled, SETTLE_MS);
        }, { passive: true });
    }

    // Touching the track is a manual takeover; the slideshow and anything
    // banked from earlier presses yield to it.
    listen(track, 'pointerdown', () => {
        forgetJump();
        // the counter may name a keypress destination we are no longer heading to
        syncChrome();
        if (slideshowOn) stopSlideshow();
    });

    // *** Track: the desktop swipe ***
    // The photo is grabbable, and a drag off it either pans the track sideways or
    // peels the photo away, whichever axis the pointer commits to first. Mouse
    // only -- touch has the browser's own panning, which carries momentum and
    // snaps on the compositor, and is not worth replacing.
    listen(track, 'dragstart', (event) => event.preventDefault());  // no ghost image

    listen(track, 'pointerdown', (event) => {
        grabbed = false;
        if (event.pointerType !== 'mouse' || event.button !== 0) return;
        if (!event.target.closest('img')) return;
        grab = {
            x: event.clientX,
            y: event.clientY,
            id: event.pointerId,
            left: track.scrollLeft,
            panel: panels[nearest()],
            axis: null,
        };
    });

    listen(track, 'pointermove', (event) => {
        if (!grab) return;
        const dx = event.clientX - grab.x;
        const dy = event.clientY - grab.y;

        if (!grab.axis) {
            if (Math.max(Math.abs(dx), Math.abs(dy)) < DRAG_START_PX) return;
            grab.axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
            // Not before now: a capture retargets the click that ends the gesture
            // to the track, and a plain click on the photo would read as a click
            // on the backdrop, which closes.
            track.setPointerCapture(grab.id);
            lightbox.classList.add('is-grabbing');
            // mandatory snapping would undo every scrollLeft below; settled() restores it
            track.classList.add('is-unsnapped');
        }

        if (grab.axis === 'x') track.scrollLeft = grab.left - dx;
        else dragPanel(grab.panel, dy);
    });

    const endGrab = (event) => {
        const start = grab;
        grab = null;
        if (!start?.axis) return;
        grabbed = true;
        lightbox.classList.remove('is-grabbing');

        if (start.axis === 'y') {
            endVerticalDrag(start.panel, event.clientY - start.y);
            return;
        }

        // Scroll to the slide the drag chose, or back to the one it left; either
        // way it is the track settling that navigates.
        const dx = event.clientX - start.x;
        if (Math.abs(dx) < SLIDE_DRAG_PX || !goTo(index + (dx < 0 ? 1 : -1))) goTo(index);
    };

    listen(track, 'pointerup', endGrab);
    listen(track, 'pointercancel', endGrab);

    // *** Touch: swipe up or down to close, the same as pressing the X ***
    listen(lightbox, 'touchstart', (event) => {
        // a caption long enough to scroll keeps its own vertical gestures, and
        // a two-finger touch is a pinch rather than a swipe
        const single = event.touches.length === 1 && !event.target.closest('figcaption');
        const touch = event.touches[0];
        swipe = single
            ? { x: touch.clientX, y: touch.clientY, left: track.scrollLeft, panel: panels[nearest()] }
            : null;
    }, { passive: true });

    listen(lightbox, 'touchmove', (event) => {
        if (!swipe) return;
        const touch = event.touches[0];
        const traveled = touch.clientY - swipe.y;
        const sideways = Math.abs(touch.clientX - swipe.x);

        // Vertical enough, far enough, and the track has stayed put: this is a
        // dismissal and not a slide swipe.
        if (!dragging) {
            if (Math.abs(traveled) < DRAG_START_PX) return;
            if (Math.abs(traveled) < sideways * CLOSE_SWIPE_RATIO) return;
            if (Math.abs(track.scrollLeft - swipe.left) > 1) return;
            dragging = true;
        }
        dragPanel(swipe.panel, traveled);
    }, { passive: true });

    listen(lightbox, 'touchcancel', () => {
        if (dragging) releasePanel(swipe.panel);
        swipe = null;
        dragging = false;
    }, { passive: true });

    listen(lightbox, 'touchend', (event) => {
        const start = swipe;
        const dragged = dragging;
        swipe = null;
        dragging = false;
        if (!dragged) return;

        endVerticalDrag(start.panel, event.changedTouches[0].clientY - start.y);
    }, { passive: true });

    // *** Window ***
    listen(window, 'resize', onResize);

    // *** Controls: closing ***
    // Clicking anywhere but the photo or a control closes.
    listen(lightbox, 'click', (event) => {
        if (grabbed) return;  // the tail end of a drag, not a click on the backdrop
        if (event.target.closest(KEEPS_OPEN)) return;
        closeLightbox();
    });

    // The X is a plain link back to the post, which is what it has to be without
    // js, so with js it needs talking out of navigating.
    listen(closeButton, 'click', (event) => {
        event.preventDefault();
        closeLightbox();
    });

    // *** Controls: the arrows ***
    const onNavClick = (event) => {
        if (!step(event.currentTarget === prevLink ? -1 : 1)) return;  // let the link do its job
        event.preventDefault();
        if (slideshowOn) stopSlideshow();
    };
    if (prevLink) listen(prevLink, 'click', onNavClick);
    if (nextLink) listen(nextLink, 'click', onNavClick);

    // *** Controls: fullscreen ***
    listen(document, 'fullscreenchange', syncFullscreen);

    // Fullscreen is requested on documentElement, not on the lightbox: the
    // lightbox is replaced on every slide change, which would drop us out of
    // fullscreen mid-slideshow.
    if (fullscreenButton) {
        listen(fullscreenButton, 'click', () => {
            const done = document.fullscreenElement
                ? document.exitFullscreen()
                : document.documentElement.requestFullscreen();
            done.catch(() => {});  // a browser refusing the request is not an error here
        });
    }

    // *** Controls: the slideshow toggle ***
    if (slideshowButton) {
        listen(slideshowButton, 'click', () => {
            if (slideshowOn) return stopSlideshow();
            if (!nextLink) return;  // nothing to advance to
            slideshowOn = true;
            setToggle(slideshowButton, true, SLIDESHOW_LABELS);
            scheduleAdvance();  // the slide you pressed play on gets its full turn
        });
    }

    // *** Keyboard ***
    listen(document, 'keydown', (event) => {
        if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return;
        let handled = false;
        if (event.key === 'ArrowLeft') handled = step(-1);
        else if (event.key === 'ArrowRight') handled = step(1);
        else if (event.key === 'Home') handled = goToPos(0);
        else if (event.key === 'End') handled = goToPos(total - 1);
        else if (event.key === 'Escape' && up.layer.isRoot()) {
            // overlays already close themselves on Escape; a directly visited
            // slide has to be sent somewhere, so send it back to the post
            closeLightbox();
            handled = true;
        }

        if (!handled) return;
        event.preventDefault();
        if (slideshowOn) stopSlideshow();
    });


    // *** STARTUP ********************************************************
    // Everything this fragment does the moment it appears. A fragment arriving
    // mid-slideshow or mid-jump also has to pick up what the one before it was
    // in the middle of, which is the second half of this section.

    panels.forEach((panel) => loadPanel(panel, listen));
    recenter();
    requestAnimationFrame(fitAll);
    document.fonts.ready.then(fitAll);  // a late webfont rewraps the text under the scrim
    syncFullscreen();

    // Show which slide we are on without leaving a trail. Nothing here carries
    // history -- modals are configured without it (main.js), the nav links opt
    // out -- so the lightbox commandeers the entry it was opened on and rewrites
    // it slide by slide. Back leaves the post outright rather than retracing it.
    up.history.replace(lightbox.dataset.url);

    // Unpoly marks its box role="dialog" but leaves it unnamed.
    if (!up.layer.isRoot()) {
        up.layer.element.querySelector('up-modal-box')?.setAttribute('aria-label', 'Lightbox');
    }

    setToggle(slideshowButton, slideshowOn, SLIDESHOW_LABELS);
    if (slideshowOn) scheduleAdvance();

    // A jump survives the swap it caused: arriving clears it, and landing short
    // of it -- which happens when the track settled first -- sends us on again.
    // A lightbox that cannot navigate discards any jump left over from one that
    // could, rather than carrying a destination it has no way of reaching.
    jumping = false;
    if (jumpTo === pos || !urlTemplate) jumpTo = null;
    else if (jumpTo !== null) jumpTimer = setTimeout(runJump, JUMP_MS);


    // *** DESTRUCTOR *****************************************************

    return () => {
        clearTimeout(timer);
        clearTimeout(advanceFallback);
        clearTimeout(debounce);
        // jumpTimer is deliberately left alone: it is shared, and the fragment
        // replacing this one may already have scheduled its own. runJump checks
        // that its lightbox is still in the document instead.
        cleanups.forEach((off) => off());
    };
});
