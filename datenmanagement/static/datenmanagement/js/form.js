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
  let buttonDisabled;
  if (window.userHasModelChangePermission)
    buttonDisabled = '';
  else
    buttonDisabled = ' disabled';
  let deleteFieldButton = $('<button class="input-reset btn btn-warning" title="Wert löschen"' + buttonDisabled + '><i class="fas fa-trash"></i></button></div>');
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
 * @name addField
 *
 * @param {Object} field - single field
 * @param {Object} fieldToInsertAfter - field after which the passed single field (i.e. its wrapper) shall be inserted
 *
 * inserts the passed single field into an array field complex
 */
function addField(field, fieldToInsertAfter) {
  // create wrapper
  let wrapper = $('<div/>', { class: 'input-group', style: 'margin-top:0.5rem' });
  // insert passed single field into created wrapper
  wrapper.append(field);
  // insert created wrapper after passed field after which the wrapper shall be inserted
  wrapper.insertAfter(fieldToInsertAfter.parent().is('.input-group') ? fieldToInsertAfter.parent() : fieldToInsertAfter);
  // add a deletion button
  addDeleteFieldButton(field);
}

/**
 * @function
 * @name adoptReverseSearchResult
 *
 * @param {JSON} geoJson - results of search for objects within a certain radius around passed coordinates
 * @param {string} addressType - address reference type (i.e. address, street or district)
 *
 * adopts results of search for objects within a certain radius around passed coordinates
 */
function adoptReverseSearchResult(geoJson, addressType) {
  let erfolg = false;
  jQuery.each(geoJson.features, function (index, item) {
    if (item.properties.objektgruppe === addressType) {
      let text = item.properties._title_.substring(item.properties._title_.lastIndexOf(', ') + 2);
      if (item.properties.gemeindeteil_abkuerzung)
        text += ' (' + item.properties.gemeindeteil_abkuerzung + ')';
      window.searchField.val(text);
      if (window.addressUuidField)
        window.addressUuidField.val(item.properties.uuid);
      erfolg = true;
      return false;
    }
  });
  if (erfolg === false)
    toggleModal(
      $('#error-modal'),
      'Keine automatische Zuordnung ' + (addressType === 'Gemeindeteil' ? 'eines ' : 'einer ') + addressType + (addressType === 'Gemeindeteil' ? 's' : '') + ' möglich!',
      'Bitte setzen Sie den Marker bzw. zeichnen Sie die Linie oder Fläche in der Karte ' + window.reverseSearchRadius + ' m oder dichter an ' + (addressType === 'Gemeindeteil' ? 'den nächsten ' : 'die nächste ') + addressType +  ' heran.'
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
 * @name cloneObject
 *
 * @param {string} url - URL
 *
 * clones the entire data set as a new data set
 */
function cloneObject(url) {
  // reset read-only fields to their defaults
  if (window.readOnlyFieldsDefaulValues) {
    for (let key in window.readOnlyFieldsDefaulValues) {
      $('form input#id_' + key).val(window.readOnlyFieldsDefaulValues[key]);
    }
  }
  $('form').attr('action', url);
}

/**
 * @function
 * @name disableValueAssigner
 *
 * @param {Object} valueAssigner - value assignment icon
 *
 * disables value assignment icon on a selection field for a foreign key
 */
function disableValueAssigner(valueAssigner) {
  valueAssigner.removeClass('text-primary enabled');
  valueAssigner.addClass('text-secondary');
  valueAssigner.attr('title', '');
}

/**
 * @function
 * @name enableAddressReferenceButton
 *
 * enables address reference (i.e. map to address, street or district) button
 */
function enableAddressReferenceButton() {
  if (window.addressType === 'Adresse')
    $('#mapToAddress').prop('disabled', false);
  else if (window.addressType === 'Straße')
    $('#mapToStreet').prop('disabled', false);
  else if (window.addressType === 'Gemeindeteil')
    $('#mapToDistrict').prop('disabled', false);
}

/**
 * @function
 * @name enablePostcodeAssigner
 *
 * enables postcode auto-assignment
 */
function enablePostcodeAssigner() {
  $('#postcode-assigner').removeClass('text-secondary');
  $('#postcode-assigner').addClass('text-primary enabled');
  $('#postcode-assigner').attr('title', 'Postleitzahl automatisch zuweisen');
}

/**
 * @function
 * @name enableValueAssigner
 *
 * @param {Object} valueAssigner - value assignment icon
 * @param {string} tooltip - tooltip
 *
 * enables value assignment icon on a selection field for a foreign key
 */
function enableValueAssigner(valueAssigner, tooltip) {
  valueAssigner.removeClass('text-secondary');
  valueAssigner.addClass('text-primary enabled');
  valueAssigner.attr('title', tooltip);
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
 * @name setAddressReference
 *
 * @param addressType - address reference type (i.e. address, street or district)
 * @param {Object} geometryLayers - layers with geometries
 *
 * adopts the current address reference of the geometries in the map
 */
function setAddressReference(addressType, geometryLayers) {
  let geoJson;
  // handle multiple geometries
  if (geometryLayers.length > 1) {
    geoJson = {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'MultiPolygon',
        coordinates: []
      }
    };
    geometryLayers.forEach((geometryLayer) => {
      let tempGeoJson = geometryLayer.toGeoJSON();
      geoJson.geometry.coordinates.push(tempGeoJson.geometry.coordinates);
    });
  } else if (typeof geometryLayers[0] !== 'undefined') {
    geoJson = geometryLayers[0].toGeoJSON();
  } else {
    geoJson = geometryLayers.toGeoJSON();
  }
  let center = L.geoJSON(geoJson).getBounds().getCenter();
  fetch(window.reverseSearchUrl + '?search_class=address&x=' + center.lng + '&y=' + center.lat, {
    method: 'GET'
  })
  .then(response => response.json())
  .then(data => {
    if (center.lng !== 0 && center.lat !== 0)
      adoptReverseSearchResult(data, addressType);
  })
  .catch(error => console.log(error))
}

/**
 * @function
 * @name setFinalArrayFields
 *
 * gets values distributed over different corresponding fields, combines them and writes them to main array fields
 */
function setFinalArrayFields() {
  // alle Array-Felder durchgehen...
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
    if (values.length > 0) {
      if (parentField.attr('type') !== 'text')
        parentField.attr('type', 'text');
      // write combined values to main array field
      parentField.val(JSON.stringify(values));
    }
  });
}

/**
 * @function
 * @name setFinalGeometry
 *
 * gets map geometry and writes it to geometry field
 */
function setFinalGeometry() {
  // the map geometry part (only if there is a map at all, though)
  if (typeof currMap !== 'undefined') {
    let jsonGeometrie;
    if (currMap.pm.getGeomanDrawLayers().length < 1) {
      let coordinates = [];
      if (window.geometryType === 'Point')
        coordinates = [0, 0];
      else if (window.geometryType === 'Polygon')
        coordinates = [[]];
      jsonGeometrie = {
        'type': window.geometryType,
        'coordinates': coordinates
      };
    } else {
      if (window.geometryType === 'MultiPolygon' || window.geometryType === 'MultiPoint' || window.geometryType === 'MultiLineString') {
        let coordinates = [];
        let temp;
        currMap.pm.getGeomanDrawLayers().forEach(function (layer) {
          temp = layer.toGeoJSON().geometry;
          if (temp.type.search('Multi') > -1) {
            for (let i = 0; i < temp.coordinates.length; i++) {
              coordinates.push(temp.coordinates[i]);
            }
          } else {
            coordinates.push(temp.coordinates);
          }
        });
        jsonGeometrie = {
          'type': window.geometryType,
          'coordinates': coordinates,
        };
      } else {
        jsonGeometrie = currMap.pm.getGeomanDrawLayers()[0].toGeoJSON().geometry;
      }
    }
    $('#id_geometrie').val(JSON.stringify(jsonGeometrie));
  }
  // the address part (only if there is an address related field at all, though)
  if (window.addressUuidField && $.trim(window.searchField.val()).length) {
    // keep current address, street or district temporarily
    window.addressTempField.val(window.searchField.val());
    // sets reference from field with UUID of the referenced address, street or district
    window.searchField.val(window.addressUuidField.val());
  }
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
    if (window.geometryType === 'Point') {
      let layer = new L.Marker(getFeatureGeometryLatLng(featureGeometry), {
        icon: redMarker
      });
      layer._drawnByGeoman = true;
      layer.addTo(window.currMap);
    }
  }
}