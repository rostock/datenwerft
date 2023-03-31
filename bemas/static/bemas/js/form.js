/* global $ */
/* eslint no-undef: "error" */

/**
 * @function
 * @name cloneObject
 *
 * @param {string} targetUrl - target URL
 *
 * clones whole object as new object
 */
function cloneObject(targetUrl) {
  $('form').attr('action', targetUrl);
}

/**
 * @function
 * @name keepDjangoRequiredMessages
 *
 * prevent HTML5/jQuery required messages from overriding Django required messages
 */
function keepDjangoRequiredMessages() {
  $('[required]').removeAttr('required');
}
