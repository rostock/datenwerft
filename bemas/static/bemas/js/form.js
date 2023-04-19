/* global $ */
/* eslint no-undef: "error" */

/**
 * @function
 * @name addDeleteFieldButton
 *
 * @param {Object} field - field
 *
 * inserts a deletion button for the given single field within an array field complex
 */
function addDeleteFieldButton(field) {
  // create button
  let deleteFieldButton = $('<button class="input-reset btn btn-warning" title="Wert löschen"><i class="fas fa-trash"></i></button></div>');
  // insert created button after given single field
  deleteFieldButton.insertAfter(field);
  // on clicking the created button...
  deleteFieldButton.click(function () {
    // delete given single field and the button itself
    field.parent().remove();
  });
}

/**
 * @function
 * @name addField
 *
 * @param {Object} field - field
 * @param {Object} fieldToInsertAfter - field after which the given single field (i.e. its wrapper) shall be inserted
 * @param {boolean} [buttonsPosition=false] - dynamically set vertical positions of buttons?
 *
 * inserts the given single field into an array field complex
 */
function addField(field, fieldToInsertAfter, buttonsPosition= false) {
  // create wrapper
  let wrapper = $('<div/>', { class: 'input-group', style: 'margin-top:0.5rem' });
  // insert given single field into created wrapper
  wrapper.append(field);
  // insert created wrapper after given field after which the wrapper shall be inserted
  wrapper.insertAfter(fieldToInsertAfter.parent().is('.input-group') ? fieldToInsertAfter.parent() : fieldToInsertAfter);
  // add a deletion button
  addDeleteFieldButton(field);
  // dynamically set vertical positions of buttons
  if (buttonsPosition)
    setButtonsPosition();
}

/**
 * @function
 * @name cleanField
 *
 * @param {Object} field - field
 * @param {number} i - current number for HTML attributes id and name of field
 * @param {string} id - base text for HTML attribute id of field
 * @param {string} name - base text for HTML attribute name of field
 *
 * cleans the given single field within an array field complex
 */
function cleanField(field, i, id, name) {
  field.attr('id', id + '_' + i);
  field.attr('name', name + '_' + i);
  field.removeAttr('is_array_field');
}

/**
 * @function
 * @name cloneObject
 *
 * @param {string} targetUrl - target URL
 *
 * clones whole object as new object by calling the given target URL
 */
function cloneObject(targetUrl) {
  $('form').attr('action', targetUrl);
}

/**
 * @function
 * @name enableAddressReferenceButton
 *
 * enables address reference (i.e. map to address) button
 */
function enableAddressReferenceButton() {
  $('#mapToAddress').prop('disabled', false);
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

/**
 * @function
 * @name setButtonsPosition
 *
 * dynamically set vertical positions of buttons by means of position and size of the form element (plus 20 pixels extra "buffer")
 */
function setButtonsPosition() {
  let top = $('#custom-form').position().top + $('#custom-form').height() + 20;
  $('#buttons').offset({
    top: top
  });
}

/**
 * @function
 * @name setFinalArrayFields
 *
 * gets values distributed over different corresponding fields, combines them and writes them to main array fields
 */
function setFinalArrayFields() {
  $('[is_array_field="true"]').each(function () {
    let parentField = $(this);
    let parentFieldId = parentField.attr('id');
    let values = [];
    // get values distributed over different corresponding fields and combine them
    // (ignoring empty fields)
    $('[id^=' + parentFieldId + ']').each(function () {
      if ($(this).val())
        values.push($(this).val());
    });
    if (values.length > 0)
      // write combined values to main array field
      parentField.val(JSON.stringify(values));
  });
}
