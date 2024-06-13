/**
 * @function
 * @name keepDjangoRequiredMessages
 *
 * prevent HTML5/jQuery required messages from overriding Django required messages
 */
function keepDjangoRequiredMessages() {
  $('[required]').removeAttr('required');
}
