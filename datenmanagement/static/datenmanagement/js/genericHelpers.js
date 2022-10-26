/**
 * @function
 * @name getFeatureCenter
 *
 * gibt das Zentrum eines übergebenen GeoJSON-Features zurück
 *
 * @param {JSON} geoJson - GeoJSON-Feature
 * @param {String} [geometryType=''] - Geometrietyp des GeoJSON-Features
 * @returns {Array} - Array mit x- und y-Koordinate
 */
function getFeatureCenter(geoJson, geometryType = '') {
  let xArray = [];
  let yArray = [];
  let ort = [];
  if (geometryType === 'Point') {
    ort = geoJson.geometry.coordinates;
  } else if (geometryType === 'LineString' || geometryType === 'Polygon') {
    Array.min = function(array) {
      return Math.min.apply(Math, array);
    };
    Array.max = function(array) {
      return Math.max.apply(Math, array);
    };
    if (geometryType === 'LineString') {
      $.each(geoJson.geometry.coordinates, function (index) {
        xArray.push(geoJson.geometry.coordinates[index][0]);
        yArray.push(geoJson.geometry.coordinates[index][1]);
      });
    } else {
      $.each(geoJson.geometry.coordinates, function (index_outer) {
        $.each(geoJson.geometry.coordinates[index_outer], function (index_inner) {
          xArray.push(geoJson.geometry.coordinates[index_outer][index_inner][0]);
          yArray.push(geoJson.geometry.coordinates[index_outer][index_inner][1]);
        });
      });
    }
    ort[0] = Array.min(xArray) + ((Array.max(xArray) - Array.min(xArray)) / 2);
    ort[1] = Array.min(yArray) + ((Array.max(yArray) - Array.min(yArray)) / 2);
  }
  return ort;
}

/**
 * @function
 * @name getFeatureGeometryLatLng
 *
 * gibt die x- und y-Koordinate (des Zentrums) einer übergebenen Geometrie eines GeoJSON-Features zurück
 *
 * @param {Object} featureGeometry - Geometrie eines GeoJSON-Features
 * @returns {Array} - Array mit x- und y-Koordinate
 */
function getFeatureGeometryLatLng(featureGeometry) {
  let x = 0, y = 0;
  if (featureGeometry.type === 'Point') {
    x = featureGeometry.coordinates[0];
    y = featureGeometry.coordinates[1];
  } else if (typeof featureGeometry.coordinates !== 'undefined') {
    x = featureGeometry.coordinates[0][1][0] + ((featureGeometry.coordinates[0][0][0] - featureGeometry.coordinates[0][1][0]) / 2);
    y = featureGeometry.coordinates[0][0][1] + ((featureGeometry.coordinates[0][2][1] - featureGeometry.coordinates[0][0][1]) / 2);
  }
  return [y, x];
}

/**
 * @function
 * @name interchangeRecursive
 *
 * rekursives Umkehren der Reihenfolge von x- und y-Koordinaten
 *
 * @param {Array} arr - Array, in dem das Umkehren der Reihenfolge durchgeführt wird
 * @param {boolean} [polygon=false] - handelt es sich um ein Polygon?
 * @returns {Array} - Array mit umgekehrter Reihenfolge von x- und y-Koordinaten
 */
function interchangeRecursive(arr, polygon = false) {
  // eindimensionales Array
  if (typeof arr[0] === 'number') {
    let lat = arr[1];
    let lng = arr[0];
    arr[0] = lat;
    arr[1] = lng;
    return arr;
  // mehrdimensionales Array
  } else if (Array.isArray(arr[0])) {
    for (let i = 0; i < arr.length; i++) {
      // bei Polygonen sind das erste und das letzte x-y-Koordinatenpaar gleich:
      // daher hier letztes x-y-Koordinatenpaar auslassen!
      if (polygon === true && i === (arr.length - 1) && typeof arr[i][0] === 'number') {
        continue;
      }
      arr[i] = interchangeRecursive(arr[i], polygon);
    }
    return arr;
  }
}

/**
 * @function
 * @name toggleModal
 *
 * schaltet die Sichtbarkeit des übergebenen Bootstrap-Modals um
 *
 * @param {Object} modal - Bootstrap-Modal
 */
function toggleModal(modal) {
  modal.modal('toggle');
}
