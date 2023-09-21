/**
 * @function
 * @name addDeleteFieldButton
 *
 * @param {Object} field - single field
 *
 * inserts a deletion button for the passed single field within an array field complex
 */
function addDeleteFieldButton(field) {
  // create button
  let deleteFieldButton = $('<button class="input-reset btn btn-warning" title="Wert löschen"><i class="fas fa-trash"></i></button></div>');
  // insert created button after passed single field
  deleteFieldButton.insertAfter(field);
  // on clicking the created button...
  deleteFieldButton.click(function () {
    // delete passed single field and the button itself
    field.parent().remove();
  });
}

/**
 * @function
 * @name addEmptyFieldButton
 *
 * @param {Object} field - field
 *
 * inserts a button after the passed field for emptying the field
 */
function addEmptyFieldButton(field) {
  // create button
  let emptyFieldButton = $('<span><i class="clear-field fas fa-circle-minus text-primary" title="alle Selektionen entfernen"></i></span>');
  // insert created button after passed field
  emptyFieldButton.insertAfter(field);
  // on clicking the created button...
  emptyFieldButton.click(function () {
    // empty passed field
    field.val([]);
  });
}

/**
 * @function
 * @name addField
 *
 * @param {Object} field - single field
 * @param {Object} fieldToInsertAfter - field after which the passed single field (i.e. its wrapper) shall be inserted
 * @param {boolean} [buttonsPosition=false] - dynamically set vertical positions of buttons?
 *
 * inserts the passed single field into an array field complex
 */
function addField(field, fieldToInsertAfter, buttonsPosition= false) {
  // create wrapper
  let wrapper = $('<div/>', { class: 'input-group', style: 'margin-top:0.5rem' });
  // insert passed single field into created wrapper
  wrapper.append(field);
  // insert created wrapper after passed field after which the wrapper shall be inserted
  wrapper.insertAfter(fieldToInsertAfter.parent().is('.input-group') ? fieldToInsertAfter.parent() : fieldToInsertAfter);
  // add a deletion button
  addDeleteFieldButton(field);
  // dynamically set vertical positions of buttons
  if (buttonsPosition)
    setButtonsPosition();
}

/**
 * @function
 * @name adoptReverseSearchResult
 *
 * @param {JSON} geoJson - results of search for objects within a certain radius around passed coordinates
 *
 * adopts results of search for objects within a certain radius around passed coordinates
 */
function adoptReverseSearchResult(geoJson) {
  let erfolg = false;
  jQuery.each(geoJson.features, function (index, item) {
    if (item.properties.objektgruppe === 'Adresse') {
      let text = item.properties._title_.substring(item.properties._title_.lastIndexOf(', ') + 2);
      if (item.properties.gemeindeteil_abkuerzung)
        text += ' (' + item.properties.gemeindeteil_abkuerzung + ')';
      searchField.val(text);
      erfolg = true;
      return false;
    }
  });
  if (erfolg === false)
    toggleModal(
      $('#error-modal'),
      'Keine automatische Zuordnung einer Adresse möglich!',
      'Bitte setzen Sie den Marker in der Karte ' + window.reverseSearchRadius + ' m oder dichter an die nächste Adresse heran.'
    );
}

/**
 * @function
 * @name cleanField
 *
 * @param {Object} field - single field
 * @param {number} i - current number for HTML attributes id and name of field
 * @param {string} id - base text for HTML attribute id of field
 * @param {string} name - base text for HTML attribute name of field
 *
 * cleans the passed single field within an array field complex
 */
function cleanField(field, i, id, name) {
  field.attr('id', id + '_' + i);
  field.attr('name', name + '_' + i);
  field.removeAttr('is_array_field');
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
 * @name setAddressToMarkerAddress
 *
 * @param {Object} layer - map layer
 * @param {string} reverseSearchBaseUrl - base URL of reverse search
 *
 * sets address to current address of map marker
 */
function setAddressToMarkerAddress(layer, reverseSearchBaseUrl) {
  let geoJson = layer.toGeoJSON();
  let geometryType = 'Point';
  let ort = getFeatureCenter(geoJson, geometryType);
  fetch(reverseSearchBaseUrl + '?search_class=address&x=' + ort[0] + '&y=' + ort[1], {
    method: 'GET'
  })
  .then(response => response.json())
  .then(data => {
    if (ort[0] !== 0 && ort[1] !== 0)
      adoptReverseSearchResult(data);
  })
  .catch(error => console.log(error))
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

/**
 * @function
 * @name setFinalGeometry
 *
 * @param {string} fieldId - geometry field id
 *
 * gets map geometry and writes it to geometry field
 */
function setFinalGeometry(fieldId) {
  let jsonGeometrie;
  if (currMap.pm.getGeomanDrawLayers().length < 1) {
    jsonGeometrie = {
      'type': 'Point',
      'coordinates': [0, 0]
    };
  } else {
    jsonGeometrie = currMap.pm.getGeomanDrawLayers()[0].toGeoJSON().geometry;
  }
  $(fieldId).val(JSON.stringify(jsonGeometrie));
}

/**
 * @function
 * @name setMarkerToAddressSearchResult
 *
 * @param {Object} map - map
 *
 * sets marker into map, located on address search result
 */
function setMarkerToAddressSearchResult(map) {
  if (map.pm.getGeomanLayers().length > 0) {
    let layer = map.pm.getGeomanLayers()[0];
    if (layer._drawnByGeoman && layer._latlng) {
      let latLng = getFeatureGeometryLatLng(featureGeometry);
      if (latLng[0] !== 0 && latLng[1] !== 0)
        layer.setLatLng(latLng);
    }
  } else {
    let layer = new L.Marker(getFeatureGeometryLatLng(featureGeometry), {
      icon: redMarker
    });
    layer._drawnByGeoman = true;
    layer.addTo(window.currMap);
  }
}
