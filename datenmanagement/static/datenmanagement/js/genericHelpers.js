/**
 * @function
 * @name interchangeRecursive
 *
 * rekursives Umkehren der Reihenfolge von x- und y-Koordinaten
 *
 * @param {Array} arr - Array, in dem das Umkehren der Reihenfolge durchgeführt wird
 * @param {boolean} [polygon=false] - handelt es sich um ein Polygon?
 * @return {Array} - Array mit umgekehrter Reihenfolge von x- und y-Koordinaten
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
