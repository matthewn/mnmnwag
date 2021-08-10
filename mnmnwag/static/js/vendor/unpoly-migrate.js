/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ([
/* 0 */,
/* 1 */
/***/ (function() {

var __spreadArray = (this && this.__spreadArray) || function (to, from) {
    for (var i = 0, il = from.length, j = to.length; i < il; i++, j++)
        to[j] = from[i];
    return to;
};
var u = up.util;
/*-
@module up.migrate
*/
up.migrate = (function () {
    var config = new up.Config(function () { return ({
        logLevel: 'warn'
    }); });
    function renamedProperty(object, oldKey, newKey) {
        var warning = function () { return warn('Property { %s } has been renamed to { %s } (found in %o)', oldKey, newKey, object); };
        return Object.defineProperty(object, oldKey, {
            get: function () {
                warning();
                return this[newKey];
            },
            set: function (newValue) {
                warning();
                this[newKey] = newValue;
            }
        });
    }
    function fixKey(object, oldKey, newKey) {
        if (u.isDefined(object[oldKey])) {
            warn('Property { %s } has been renamed to { %s } (found in %o)', oldKey, newKey, object);
            u.renameKey(object, oldKey, newKey);
        }
    }
    // Maps old event type to new event type
    var renamedEvents = {};
    function renamedEvent(oldType, newType) {
        renamedEvents[oldType] = newType;
    }
    function fixEventType(eventType) {
        var newEventType = renamedEvents[eventType];
        if (newEventType) {
            warn("Event " + eventType + " has been renamed to " + newEventType);
            return newEventType;
        }
        else {
            return eventType;
        }
    }
    function fixEventTypes(eventTypes) {
        // Remove duplicates as e.g. up:history:pushed and up:history:replaced
        // both map to up:location:changed.
        return u.uniq(u.map(eventTypes, fixEventType));
    }
    function renamedPackage(oldName, newName) {
        Object.defineProperty(up, oldName, {
            get: function () {
                warn("up." + oldName + " has been renamed to up." + newName);
                return up[newName];
            }
        });
    }
    var warnedMessages = {};
    function warn(message) {
        var _a;
        var args = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args[_i - 1] = arguments[_i];
        }
        var formattedMessage = u.sprintf.apply(u, __spreadArray([message], args));
        if (!warnedMessages[formattedMessage]) {
            warnedMessages[formattedMessage] = true;
            (_a = up.log)[config.logLevel].apply(_a, __spreadArray(['unpoly-migrate', message], args));
        }
    }
    function deprecated(deprecatedExpression, replacementExpression) {
        warn(deprecatedExpression + " has been deprecated. Use " + replacementExpression + " instead.");
    }
    // Returns a resolved promise that prints a warning when #then() is called.
    function formerlyAsync(label) {
        var promise = Promise.resolve();
        var oldThen = promise.then;
        promise.then = function () {
            warn(label + " is now a sync function");
            return oldThen.apply(this, arguments);
        };
        return promise;
    }
    function reset() {
        config.reset();
    }
    up.on('up:framework:reset', reset);
    return {
        deprecated: deprecated,
        renamedPackage: renamedPackage,
        renamedProperty: renamedProperty,
        formerlyAsync: formerlyAsync,
        renamedEvent: renamedEvent,
        fixEventTypes: fixEventTypes,
        fixKey: fixKey,
        warn: warn,
        loaded: true,
        config: config
    };
})();


/***/ }),
/* 2 */
/***/ (function() {

/*-
@module up.util
*/
/*-
Returns a copy of the given object that only contains
the given keys.

@function up.util.only
@param {Object} object
@param {Array} ...keys
@deprecated
  Use `up.util.pick()` instead.
*/
up.util.only = function (object) {
    var keys = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        keys[_i - 1] = arguments[_i];
    }
    up.migrate.deprecated('up.util.only(object, ...keys)', 'up.util.pick(object, keys)');
    return up.util.pick(object, keys);
};
/*-
Returns a copy of the given object that contains all except
the given keys.

@function up.util.except
@param {Object} object
@param {Array} ...keys
@deprecated
  Use `up.util.omit(object, keys)` (with an array argument) instead of `up.util.object(...keys)` (with rest arguments).
*/
up.util.except = function (object) {
    var keys = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        keys[_i - 1] = arguments[_i];
    }
    up.migrate.deprecated('up.util.except(object, ...keys)', 'up.util.omit(object, keys)');
    return up.util.omit(object, keys);
};
up.util.parseUrl = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.parseUrl() has been renamed to up.util.parseURL()');
    return (_a = up.util).parseURL.apply(_a, args);
};
up.util.any = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.any() has been renamed to up.util.some()');
    return (_a = up.util).some.apply(_a, args);
};
up.util.all = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.all() has been renamed to up.util.every()');
    return (_a = up.util).every.apply(_a, args);
};
up.util.detect = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.detect() has been renamed to up.util.find()');
    return (_a = up.util).find.apply(_a, args);
};
up.util.select = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.select() has been renamed to up.util.filter()');
    return (_a = up.util).filter.apply(_a, args);
};
up.util.setTimer = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.setTimer() has been renamed to up.util.timer()');
    return (_a = up.util).timer.apply(_a, args);
};
up.util.escapeHtml = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.util.escapeHtml', 'up.util.escapeHTML');
    return (_a = up.util).escapeHTML.apply(_a, args);
};
up.util.selectorForElement = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.selectorForElement() has been renamed to up.fragment.toTarget()');
    return (_a = up.fragment).toTarget.apply(_a, args);
};
up.util.nextFrame = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.warn('up.util.nextFrame() has been renamed to up.util.task()');
    return (_a = up.util).task.apply(_a, args);
};
/*-
Calls the given function for the given number of times.

@function up.util.times
@param {number} count
@param {Function()} block
@deprecated
  Use a `for` loop instead.
*/
up.util.times = function (count, block) {
    for (var i = 0; i < count; i++) {
        block();
    }
};


/***/ }),
/* 3 */
/***/ (function() {

/*-
@module up.element
*/
/*-
Returns the first descendant element matching the given selector.

@function up.element.first
@param {Element} [parent=document]
  The parent element whose descendants to search.

  If omitted, all elements in the `document` will be searched.
@param {string} selector
  The CSS selector to match.
@return {Element|undefined|null}
  The first element matching the selector.

  Returns `null` or `undefined` if no element macthes.
@deprecated
  Use `up.element.get()` instead.
*/
up.element.first = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.element.first()', 'up.element.get()');
    return (_a = up.element).get.apply(_a, args);
};
up.element.createFromHtml = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.element.createFromHtml', 'up.element.createFromHTML');
    return (_a = up.element).createFromHTML.apply(_a, args);
};


/***/ }),
/* 4 */
/***/ (function() {

/*-
@module up.event
*/
up.migrate.renamedPackage('bus', 'event');
/*-
[Emits an event](/up.emit) and returns whether no listener
has prevented the default action.

### Example

```javascript
if (up.event.nobodyPrevents('disk:erase')) {
  Disk.erase()
})
```

@function up.event.nobodyPrevents
@param {string} eventType
@param {Object} eventProps
@return {boolean}
  whether no listener has prevented the default action
@deprecated
  Use `!up.emit(type).defaultPrevented` instead.
*/
up.event.nobodyPrevents = function () {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.event.nobodyPrevents(type)', '!up.emit(type).defaultPrevented');
    var event = up.emit.apply(up, args);
    return !event.defaultPrevented;
};


/***/ }),
/* 5 */
/***/ (function() {

var u = up.util;
var e = up.element;
up.migrate.postCompile = function (elements, compiler) {
    // up.compiler() has a legacy { keep } option that will automatically
    // set [up-keep] on the elements it compiles
    var keepValue;
    if (keepValue = compiler.keep) {
        up.migrate.warn('The { keep: true } option for up.compiler() has been removed. Have the compiler set [up-keep] attribute instead.');
        var value = u.isString(keepValue) ? keepValue : '';
        for (var _i = 0, elements_1 = elements; _i < elements_1.length; _i++) {
            var element = elements_1[_i];
            element.setAttribute('up-keep', value);
        }
    }
};
up.migrate.targetMacro = function (queryAttr, fixedResultAttrs, callback) {
    up.macro("[" + queryAttr + "]", function (link) {
        var optionalTarget;
        var resultAttrs = u.copy(fixedResultAttrs);
        if ((optionalTarget = link.getAttribute(queryAttr))) {
            resultAttrs['up-target'] = optionalTarget;
        }
        else {
            resultAttrs['up-follow'] = '';
        }
        e.setMissingAttrs(link, resultAttrs);
        link.removeAttribute(queryAttr);
        callback === null || callback === void 0 ? void 0 : callback();
    });
};


/***/ }),
/* 6 */
/***/ (function() {

/*-
@module up.form
*/
up.migrate.renamedProperty(up.form.config, 'fields', 'fieldSelectors');
up.migrate.renamedProperty(up.form.config, 'submitButtons', 'submitButtonSelectors');


/***/ }),
/* 7 */
/***/ (function() {

var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var u = up.util;
/*-
@module up.fragment
*/
up.migrate.renamedPackage('flow', 'fragment');
up.migrate.renamedPackage('dom', 'fragment');
up.migrate.renamedProperty(up.fragment.config, 'fallbacks', 'mainTargets');
up.migrate.handleResponseDocOptions = function (docOptions) { return up.migrate.fixKey(docOptions, 'html', 'document'); };
/*-
Replaces elements on the current page with corresponding elements
from a new page fetched from the server.

@function up.replace
@param {string|Element|jQuery} target
  The CSS selector to update. You can also pass a DOM element or jQuery element
  here, in which case a selector will be inferred from the element's class and ID.
@param {string} url
  The URL to fetch from the server.
@param {Object} [options]
  See `options` for `up.render()`.
@return {Promise}
  A promise that fulfills when the page has been updated.
@deprecated
  Use `up.render()` or `up.navigate()` instead.
*/
up.replace = function (target, url, options) {
    up.migrate.deprecated('up.replace(target, url)', 'up.navigate(target, { url })');
    return up.navigate(__assign(__assign({}, options), { target: target, url: url }));
};
/*-
Updates a selector on the current page with the
same selector from the given HTML string.

### Example

Let's say your current HTML looks like this:

    <div class="one">old one</div>
    <div class="two">old two</div>

We now replace the second `<div>`, using an HTML string
as the source:

    html = '<div class="one">new one</div>' +
           '<div class="two">new two</div>'

    up.extract('.two', html)

Unpoly looks for the selector `.two` in the strings and updates its
contents in the current page. The current page now looks like this:

    <div class="one">old one</div>
    <div class="two">new two</div>

Note how only `.two` has changed. The update for `.one` was
discarded, since it didn't match the selector.

@function up.extract
@param {string|Element|jQuery} target
@param {string} html
@param {Object} [options]
  See options for [`up.render()`](/up.render).
@return {Promise}
  A promise that will be fulfilled when the selector was updated.
@deprecated
  Use `up.render()` or `up.navigate()` instead.
*/
up.extract = function (target, document, options) {
    up.migrate.deprecated('up.extract(target, document)', 'up.navigate(target, { document })');
    return up.navigate(__assign(__assign({}, options), { target: target, document: document }));
};
/*-
Returns the first element matching the given selector, but
ignores elements that are being [destroyed](/up.destroy) or that are being
removed by a [transition](/up.morph).

Returns `undefined` if no element matches these conditions.

@function up.fragment.first
@param {Element|jQuery} [root=document]
  The root element for the search. Only the root's children will be matched.

  May be omitted to search through all elements in the `document`.
@param {string} selector
  The selector to match
@param {string} [options.layer='current']
  The the layer in which to find the element.

  @see layer-option
@param {string|Element|jQuery} [options.origin]
  An second element or selector that can be referenced as `:origin` in the first selector:
@return {Element|undefined}
  The first element that is neither a ghost or being destroyed,
  or `undefined` if no such element was found.
@deprecated
  Use `up.fragment.get()` instead.
*/
up.fragment.first = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.fragment.first()', 'up.fragment.get()');
    return (_a = up.fragment).get.apply(_a, args);
};
up.first = up.fragment.first;
up.migrate.handleScrollOptions = function (options) {
    if (u.isUndefined(options.scroll)) {
        // Rewrite deprecated { reveal } option (it had multiple variants)
        if (u.isString(options.reveal)) {
            up.migrate.deprecated("Option { reveal: '" + options.reveal + "' }", "{ scroll: '" + options.reveal + "' }");
            options.scroll = options.reveal;
        }
        else if (options.reveal === true) {
            up.migrate.deprecated('Option { reveal: true }', "{ scroll: 'target' }");
            options.scroll = 'target';
        }
        else if (options.reveal === false) {
            up.migrate.deprecated('Option { reveal: false }', "{ scroll: false }");
            options.scroll = false;
        }
        // Rewrite deprecated { resetScroll } option
        if (u.isDefined(options.resetScroll)) {
            up.migrate.deprecated('Option { resetScroll: true }', "{ scroll: 'reset' }");
            options.scroll = 'teset';
        }
        // Rewrite deprecated { restoreScroll } option
        if (u.isDefined(options.restoreScroll)) {
            up.migrate.deprecated('Option { restoreScroll: true }', "{ scroll: 'restore' }");
            options.scroll = 'restore';
        }
    }
};
up.migrate.handleHistoryOption = function (options) {
    if (u.isString(options.history) && (options.history !== 'auto')) {
        up.migrate.warn("Passing a URL as { history } option is deprecated. Pass it as { location } instead.");
        options.location = options.history;
        // Also the URL in { history } is truthy, keeping a value in there would also inherit to failOptions,
        // where it would be expanded to { failLocation }.
        options.history = 'auto';
    }
};
up.migrate.preprocessRenderOptions = function (options) {
    up.migrate.handleHistoryOption(options);
    for (var _i = 0, _a = ['target', 'origin']; _i < _a.length; _i++) {
        var prop = _a[_i];
        if (u.isJQuery(options[prop])) {
            up.migrate.warn('Passing a jQuery collection as { %s } is deprecated. Pass it as a native element instead.', prop);
            options[prop] = up.element.get(options[prop]);
        }
    }
};


/***/ }),
/* 8 */
/***/ (function() {

/*-
@module up.history
*/
up.migrate.renamedProperty(up.history.config, 'popTargets', 'restoreTargets');
/*-
Returns a normalized URL for the current history entry.

@function up.history.url
@return {string}
@deprecated Use the `up.history.location` property instead.
*/
up.history.url = function () {
    up.migrate.deprecated('up.history.url()', 'up.history.location');
    return up.history.location;
};
up.migrate.renamedEvent('up:history:push', 'up:location:changed');
up.migrate.renamedEvent('up:history:pushed', 'up:location:changed');
up.migrate.renamedEvent('up:history:restore', 'up:location:changed');
up.migrate.renamedEvent('up:history:restored', 'up:location:changed');
// There was never an up:history:replace (present tense) event
up.migrate.renamedEvent('up:history:replaced', 'up:location:changed');


/***/ }),
/* 9 */
/***/ (function() {

/*-
@module up.feedback
*/
up.migrate.renamedPackage('navigation', 'feedback');
up.migrate.renamedProperty(up.feedback.config, 'navs', 'navSelectors');


/***/ }),
/* 10 */
/***/ (function() {

/*-
@module up.link
*/
up.migrate.parseFollowOptions = function (parser) {
    parser.string('flavor'); // Renamed to { mode }.
    parser.string('width'); // Removed overlay option.
    parser.string('height'); // Removed overlay option.
    parser.boolean('closable'); // Renamed to { dismissable }.
    parser.booleanOrString('reveal'); // legacy option for { scroll: 'target' }
    parser.boolean('resetScroll'); // legacy option for { scroll: 'top' }
    parser.boolean('restoreScroll'); // legacy option for { scroll: 'restore' }
    parser.booleanOrString('historyVisible'); // short-lived legacy option for { history }
};
/*-
[Follows](/up.follow) this link as fast as possible.

This is done by:

- [Following the link through AJAX](/a-up-follow) instead of a full page load
- [Preloading the link's destination URL](/a-up-preload)
- [Triggering the link on `mousedown`](/a-up-instant) instead of on `click`

### Example

Use `[up-dash]` like this:

    <a href="/users" up-dash=".main">User list</a>

This is shorthand for:

    <a href="/users" up-target=".main" up-instant up-preload>User list</a>

@selector a[up-dash]
@param [up-dash='body']
  The CSS selector to replace

  Inside the CSS selector you may refer to this link as `&` ([like in Sass](https://sass-lang.com/documentation/file.SASS_REFERENCE.html#parent-selector)).
@deprecated
  To accelerate all links use `up.link.config.instantSelectors` and `up.link.config.preloadSelectors`.
*/
up.migrate.targetMacro('up-dash', { 'up-preload': '', 'up-instant': '' }, function () { return up.migrate.deprecated('a[up-dash]', 'up.link.config.instantSelectors or up.link.config.preloadSelectors'); });


/***/ }),
/* 11 */
/***/ (function() {

/*-
@module up.layer
*/
up.migrate.handleLayerOptions = function (options) {
    up.migrate.fixKey(options, 'flavor', 'mode');
    up.migrate.fixKey(options, 'closable', 'dismissable');
    up.migrate.fixKey(options, 'closeLabel', 'dismissLabel');
    for (var _i = 0, _a = ['width', 'maxWidth', 'height']; _i < _a.length; _i++) {
        var dimensionKey = _a[_i];
        if (options[dimensionKey]) {
            up.migrate.warn("Layer option { " + dimensionKey + " } has been removed. Use { size } or { class } instead.");
        }
    }
    if (options.sticky) {
        up.migrate.warn('Layer option { sticky } has been removed. Give links an [up-peel=false] attribute to prevent layer dismissal on click.');
    }
    if (options.template) {
        up.migrate.warn('Layer option { template } has been removed. Use { class } or modify the layer HTML on up:layer:open.');
    }
    if (options.layer === 'page') {
        up.migrate.warn("Option { layer: 'page' } has been renamed to { layer: 'root' }.");
        options.layer = 'root';
    }
    if ((options.layer === 'modal') || (options.layer === 'popup')) {
        up.migrate.warn("Option { layer: '" + options.layer + "' } has been removed. Did you mean { layer: 'overlay' }?");
        options.layer = 'overlay';
    }
};
up.migrate.handleTetherOptions = function (options) {
    var _a = options.position.split('-'), position = _a[0], align = _a[1];
    if (align) {
        up.migrate.warn('The position value %o is deprecated. Use %o instead.', options.position, { position: position, align: align });
        options.position = position;
        options.align = align;
    }
};
/*-
When this element is clicked, closes a currently open overlay.

Does nothing if no overlay is currently open.

To make a link that closes the current overlay, but follows to
a fallback destination on the root layer:

    <a href="/fallback" up-close>Okay</a>

@selector a[up-close]
@deprecated
  Use `a[up-dismiss]` instead.
*/
up.migrate.registerLayerCloser = function (layer) {
    return layer.registerClickCloser('up-close', function (value, closeOptions) {
        up.migrate.deprecated('[up-close]', '[up-dismiss]');
        layer.dismiss(value, closeOptions);
    });
};
up.migrate.handleLayerConfig = function (config) { return up.migrate.fixKey(config, 'historyVisible', 'history'); };
up.util.getter(up.Layer.prototype, 'historyVisible', function () {
    up.migrate.deprecated('up.Layer#historyVisible', 'up.Layer#history');
    return this.history;
});


/***/ }),
/* 12 */
/***/ (function() {

/*-
@module up.layer
*/
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var FLAVORS_ERROR = new Error('up.modal.flavors has been removed without direct replacement. You may give new layers a { class } or modify layer elements on up:layer:open.');
up.modal = {
    /*-
    Opens a modal overlay for the given URL.
  
    @function up.modal.visit
    @param {string} url
      The URL to load.
    @param {Object} options
      See options for `up.render()`.
    @deprecated
      Use `up.layer.open({ url, mode: "modal" })` instead.
    */
    visit: function (url, options) {
        if (options === void 0) { options = {}; }
        up.migrate.deprecated('up.modal.visit(url)', 'up.layer.open({ url, mode: "modal" })');
        return up.layer.open(__assign(__assign({}, options), { url: url, mode: 'modal' }));
    },
    /*-
    Opens the given link's destination in a modal overlay.
  
    @function up.modal.follow
    @param {Element|jQuery|string} linkOrSelector
      The link to follow.
    @param {string} [options]
      See options for `up.render()`.
    @return {Promise}
      A promise that will be fulfilled when the modal has been opened.
    @deprecated
      Use `up.follow(link, { layer: "modal" })` instead.
    */
    follow: function (link, options) {
        if (options === void 0) { options = {}; }
        up.migrate.deprecated('up.modal.follow(link)', 'up.follow(link, { layer: "modal" })');
        return up.follow(link, __assign(__assign({}, options), { layer: 'modal' }));
    },
    /*-
    [Extracts](/up.extract) the given CSS selector from the given HTML string and
    opens the results in a modal overlay.
  
    @function up.modal.extract
    @param {string} selector
      The CSS selector to extract from the HTML.
    @param {string} document
      The HTML containing the modal content.
    @param {Object} options
      See options for [`up.modal.follow()`](/up.modal.follow).
    @return {Promise}
      A promise that will be fulfilled when the modal has been opened.
    @deprecated
      Use `up.layer.open({ document, mode: "modal" })` instead.
    */
    extract: function (target, html, options) {
        if (options === void 0) { options = {}; }
        up.migrate.deprecated('up.modal.extract(target, document)', 'up.layer.open({ document, mode: "modal" })');
        return up.layer.open(__assign(__assign({}, options), { target: target, html: html, layer: 'modal' }));
    },
    /*-
    Closes a currently open overlay.
  
    @function up.modal.close
    @param {Object} options
    @return {Promise}
    @deprecated
      Use `up.layer.dismiss()` instead.
    */
    close: function (options) {
        if (options === void 0) { options = {}; }
        up.migrate.deprecated('up.modal.close()', 'up.layer.dismiss()');
        up.layer.dismiss(null, options);
        return up.migrate.formerlyAsync('up.layer.dismiss()');
    },
    /*-
    Returns the location URL of the fragment displayed in the current overlay.
  
    @function up.modal.url
    @return {string}
    @deprecated
      Use `up.layer.location` instead.
    */
    url: function () {
        up.migrate.deprecated('up.modal.url()', 'up.layer.location');
        return up.layer.location;
    },
    /*-
    Returns the location URL of the layer behind the current overlay.
  
    @function up.modal.coveredUrl
    @return {string}
    @deprecated
      Use `up.layer.parent.location` instead.
    */
    coveredUrl: function () {
        var _a;
        up.migrate.deprecated('up.modal.coveredUrl()', 'up.layer.parent.location');
        return (_a = up.layer.parent) === null || _a === void 0 ? void 0 : _a.location;
    },
    /*-
    Sets default options for future modal overlays.
  
    @property up.modal.config
    @deprecated
      Use `up.layer.config.modal` instead.
    */
    get config() {
        up.migrate.deprecated('up.modal.config', 'up.layer.config.modal');
        return up.layer.config.modal;
    },
    /*-
    Returns whether the given element or selector is contained
    within the current layer.
  
    @function up.modal.contains
    @param {string} elementOrSelector
      The element to test
    @return {boolean}
    @deprecated
      Use `up.layer.contains()` instead.
    */
    contains: function (element) {
        up.migrate.deprecated('up.modal.contains()', 'up.layer.contains()');
        return up.layer.contains(element);
    },
    /*-
    Returns whether an overlay is currently open.
  
    @function up.modal.isOpen
    @return {boolean}
    @deprecated
      Use `up.layer.isOverlay()` instead.
    */
    isOpen: function () {
        up.migrate.deprecated('up.modal.isOpen()', 'up.layer.isOverlay()');
        return up.layer.isOverlay();
    },
    get flavors() {
        throw FLAVORS_ERROR;
    },
    flavor: function () {
        throw FLAVORS_ERROR;
    }
};
up.migrate.renamedEvent('up:modal:open', 'up:layer:open');
up.migrate.renamedEvent('up:modal:opened', 'up:layer:opened');
up.migrate.renamedEvent('up:modal:close', 'up:layer:dismiss');
up.migrate.renamedEvent('up:modal:closed', 'up:layer:dismissed');
/*-
Clicking this link will load the destination via AJAX and open
the given selector in a modal overlay.

@selector a[up-modal]
@params-note
  All attributes for `a[up-layer=new]` may also be used.
@param {string} up-modal
  The CSS selector that will be extracted from the response and displayed in a modal dialog.
@deprecated
  Use `a[up-layer="new modal"]` instead.
*/
up.migrate.targetMacro('up-modal', { 'up-layer': 'new modal' }, function () { return up.migrate.deprecated('a[up-modal]', 'a[up-layer="new modal"]'); });
/*-
Clicking this link will load the destination via AJAX and open
the given selector in a modal drawer that slides in from the edge of the screen.

@selector a[up-drawer]
@params-note
  All attributes for `a[up-layer=new]` may also be used.
@param {string} up-drawer
  The CSS selector that will be extracted from the response and displayed in a modal dialog.
@deprecated
  Use `a[up-layer="new drawer"]` instead.
*/
up.migrate.targetMacro('up-drawer', { 'up-layer': 'new drawer' }, function () { return up.migrate.deprecated('a[up-drawer]', 'a[up-layer="new drawer"]'); });


/***/ }),
/* 13 */
/***/ (function() {

/*-
@module up.layer
*/
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
up.popup = {
    /*-
    Attaches a popup overlay to the given element or selector.
  
    @function up.popup.attach
    @param {Element|jQuery|string} anchor
      The element to which the popup will be attached.
    @param {Object} [options]
      See options for `up.render()`.
    @return {Promise}
    @deprecated
      Use `up.layer.open({ origin, layer: 'popup' })` instead.
    */
    attach: function (origin, options) {
        if (options === void 0) { options = {}; }
        origin = up.fragment.get(origin);
        up.migrate.deprecated('up.popup.attach(origin)', "up.layer.open({ origin, layer: 'popup' })");
        return up.layer.open(__assign(__assign({}, options), { origin: origin, layer: 'popup' }));
    },
    /*-
    Closes a currently open overlay.
  
    @function up.popup.close
    @param {Object} options
    @return {Promise}
    @deprecated
      Use `up.layer.dismiss()` instead.
    */
    close: function (options) {
        if (options === void 0) { options = {}; }
        up.migrate.deprecated('up.popup.close()', 'up.layer.dismiss()');
        up.layer.dismiss(null, options);
        return up.migrate.formerlyAsync('up.layer.dismiss()');
    },
    /*-
    Returns the location URL of the fragment displayed in the current overlay.
  
    @function up.popup.url
    @return {string}
    @deprecated
      Use `up.layer.location` instead.
    */
    url: function () {
        up.migrate.deprecated('up.popup.url()', 'up.layer.location');
        return up.layer.location;
    },
    /*-
    Returns the location URL of the layer behind the current overlay.
  
    @function up.popup.coveredUrl
    @return {string}
    @deprecated
      Use `up.layer.parent.location` instead.
    */
    coveredUrl: function () {
        var _a;
        up.migrate.deprecated('up.popup.coveredUrl()', 'up.layer.parent.location');
        return (_a = up.layer.parent) === null || _a === void 0 ? void 0 : _a.location;
    },
    /*-
    Sets default options for future popup overlays.
  
    @property up.popup.config
    @deprecated
      Use `up.layer.config.popup` instead.
    */
    get config() {
        up.migrate.deprecated('up.popup.config', 'up.layer.config.popup');
        return up.layer.config.popup;
    },
    /*-
    Returns whether the given element or selector is contained
    within the current layer.
  
    @function up.popup.contains
    @param {string} elementOrSelector
      The element to test
    @return {boolean}
    @deprecated
      Use `up.layer.contains()` instead.
    */
    contains: function (element) {
        up.migrate.deprecated('up.popup.contains()', 'up.layer.contains()');
        return up.layer.contains(element);
    },
    /*-
    Returns whether an overlay is currently open.
  
    @function up.popup.isOpen
    @return {boolean}
    @deprecated
      Use `up.layer.isOverlay()` instead.
    */
    isOpen: function () {
        up.migrate.deprecated('up.popup.isOpen()', 'up.layer.isOverlay()');
        return up.layer.isOverlay();
    },
    sync: function () {
        up.migrate.deprecated('up.popup.sync()', 'up.layer.sync()');
        return up.layer.sync();
    }
};
up.migrate.renamedEvent('up:popup:open', 'up:layer:open');
up.migrate.renamedEvent('up:popup:opened', 'up:layer:opened');
up.migrate.renamedEvent('up:popup:close', 'up:layer:dismiss');
up.migrate.renamedEvent('up:popup:closed', 'up:layer:dismissed');
up.migrate.targetMacro('up-popup', { 'up-layer': 'new popup' }, function () { return up.migrate.deprecated('[up-popup]', '[up-layer="new popup"]'); });


/***/ }),
/* 14 */
/***/ (function() {

/*-
Tooltips
========

Unpoly used to come with a basic tooltip implementation.
This feature is now deprecated.

@module up.tooltip
*/
up.macro('[up-tooltip]', function (opener) {
    up.migrate.warn('[up-tooltip] has been deprecated. A [title] was set instead.');
    up.element.setMissingAttr(opener, 'title', opener.getAttribute('up-tooltip'));
});


/***/ }),
/* 15 */
/***/ (function() {

var u = up.util;
/*-
@module up.network
*/
up.migrate.renamedPackage('proxy', 'network');
up.migrate.renamedEvent('up:proxy:load', 'up:request:load'); // renamed in 1.0.0
up.migrate.renamedEvent('up:proxy:received', 'up:request:loaded'); // renamed in 0.50.0
up.migrate.renamedEvent('up:proxy:loaded', 'up:request:loaded'); // renamed in 1.0.0
up.migrate.renamedEvent('up:proxy:fatal', 'up:request:fatal'); // renamed in 1.0.0
up.migrate.renamedEvent('up:proxy:aborted', 'up:request:aborted'); // renamed in 1.0.0
up.migrate.renamedEvent('up:proxy:slow', 'up:request:late'); // renamed in 1.0.0
up.migrate.renamedEvent('up:proxy:recover', 'up:request:recover'); // renamed in 1.0.0
var preloadDelayMoved = function () { return up.migrate.deprecated('up.proxy.config.preloadDelay', 'up.link.config.preloadDelay'); };
Object.defineProperty(up.network.config, 'preloadDelay', {
    get: function () {
        preloadDelayMoved();
        return up.link.config.preloadDelay;
    },
    set: function (value) {
        preloadDelayMoved();
        up.link.config.preloadDelay = value;
    }
});
up.migrate.renamedProperty(up.network.config, 'maxRequests', 'concurrency');
up.migrate.renamedProperty(up.network.config, 'slowDelay', 'badResponseTime');
up.migrate.handleRequestOptions = function (options) { return up.migrate.fixKey(options, 'data', 'params'); };
/*-
Makes an AJAX request to the given URL and caches the response.

The function returns a promise that fulfills with the response text.

### Example

```
up.ajax('/search', { params: { query: 'sunshine' } }).then(function(text) {
  console.log('The response text is %o', text)
}).catch(function() {
  console.error('The request failed')
})
```

@function up.ajax
@param {string} [url]
  The URL for the request.

  Instead of passing the URL as a string argument, you can also pass it as an `{ url }` option.
@param {Object} [options]
  See options for `up.request()`.
@return {Promise<string>}
  A promise for the response text.
@deprecated
  Use `up.request()` instead.
*/
up.ajax = function () {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.ajax()', 'up.request()');
    var pickResponseText = function (response) { return response.text; };
    return up.request.apply(up, args).then(pickResponseText);
};
/*-
Removes all cache entries.

@function up.proxy.clear
@deprecated
  Use `up.cache.clear()` instead.
*/
up.network.clear = function () {
    up.migrate.deprecated('up.proxy.clear()', 'up.cache.clear()');
    up.cache.clear();
};
up.network.preload = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.proxy.preload(link)', 'up.link.preload(link)');
    return (_a = up.link).preload.apply(_a, args);
};
/*-
@class up.Request
*/
up.Request.prototype.navigate = function () {
    up.migrate.deprecated('up.Request#navigate()', 'up.Request#loadPage()');
    this.loadPage();
};
/*-
@class up.Response
*/
/*-
Returns whether the server responded with a 2xx HTTP status.

@function up.Response#isSuccess
@return {boolean}
@deprecated
  Use `up.Response#ok` instead.
*/
up.Response.prototype.isSuccess = function () {
    up.migrate.deprecated('up.Response#isSuccess()', 'up.Response#ok');
    return this.ok;
};
/*-
Returns whether the response was not [successful](/up.Response.prototype.ok).

@function up.Response#isError
@return {boolean}
@deprecated
  Use `!up.Response#ok` instead.
*/
up.Response.prototype.isError = function () {
    up.migrate.deprecated('up.Response#isError()', '!up.Response#ok');
    return !this.ok;
};
function mayHaveCustomIndicator() {
    var listeners = up.EventListener.allNonDefault(document);
    return u.find(listeners, function (listener) { return listener.eventType === 'up:request:late'; });
}
var progressBarDefault = up.network.config.progressBar;
function disableProgressBarIfCustomIndicator() {
    up.network.config.progressBar = function () {
        if (mayHaveCustomIndicator()) {
            up.migrate.warn('Disabled the default progress bar as may have built a custom loading indicator with your up:request:late listener. Please set up.network.config.progressBar to true or false.');
            return false;
        }
        else {
            return progressBarDefault;
        }
    };
}
disableProgressBarIfCustomIndicator();
up.on('up:framework:reset', disableProgressBarIfCustomIndicator);


/***/ }),
/* 16 */
/***/ (function() {

/*-
@module up.radio
*/
up.migrate.renamedProperty(up.radio.config, 'hungry', 'hungrySelectors');


/***/ }),
/* 17 */
/***/ (function() {

/*-
@module up.viewport
*/
up.migrate.renamedPackage('layout', 'viewport');
up.migrate.renamedProperty(up.viewport.config, 'viewports', 'viewportSelectors');
up.migrate.renamedProperty(up.viewport.config, 'snap', 'revealSnap');
/*-
Returns the scrolling container for the given element.

Returns the [document's scrolling element](/up.viewport.root)
if no closer viewport exists.

@function up.viewport.closest
@param {string|Element|jQuery} target
@return {Element}
@deprecated
  Use `up.viewport.get()` instead.
*/
up.viewport.closest = function () {
    var _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    up.migrate.deprecated('up.viewport.closest()', 'up.viewport.get()');
    return (_a = up.viewport).get.apply(_a, args);
};


/***/ })
/******/ 	]);
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
!function() {
// We are going to add compilers and event handlers that should not be reset during specs.
up.framework.startExtension();
__webpack_require__(1);
__webpack_require__(2);
__webpack_require__(3);
__webpack_require__(4);
__webpack_require__(5);
__webpack_require__(6);
__webpack_require__(7);
__webpack_require__(8);
__webpack_require__(9);
__webpack_require__(10);
__webpack_require__(11);
__webpack_require__(12);
__webpack_require__(13);
__webpack_require__(14);
__webpack_require__(15);
__webpack_require__(16);
__webpack_require__(17);
up.framework.stopExtension();

}();
/******/ })()
;