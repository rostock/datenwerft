/**
 * @function
 * @name getArrayDepth
 *
 * Gibt Tiefe eines n-dimensionalen Arrays zurück.
 *
 * @param value - Array
 * @returns {number|number}
 */
function getArrayDepth(value) {
  return Array.isArray(value) ?
    1 + Math.max(...value.map(getArrayDepth)) :
    0;
}


/**
 * @function
 * @name nDimensionalSearch
 *
 * Rekursives Durchsuchen eines n-dimensionalen Arrays
 *
 * @param arr - n-dimensionales Array, welches durchsucht wird
 * @param obj - Objekt nach dem gesucht wird
 * @param position - aktuelle Position: für rekursive Aufrufe
 */
function nDimensionalSearch(arr, obj, position=[]) {
  let i = arr.indexOf(obj);
  if (i !== -1) {
    position.push(i);
    return position;
  } else if (Array.isArray(arr)){
    for (let j = 0; j < arr.length; j++) {
      position.push(j)
      nDimensionalSearch(arr[j], obj, position)
      position.pop();
    }
  } else {
    position = [];
  }
  return position;
}

function interchangeRekursiv(arr, polygon=false) {
  if (typeof arr[0] === 'number'){
    let lat = arr[1];
    let lng = arr[0];
    arr[0] = lat;
    arr[1] = lng;
    return arr;
  } else if (Array.isArray(arr[0])) {
    for (let i = 0; i < arr.length; i++) {
      // erste und letzte Koordinate sind selbes Objekt: darf nur einmal bearbeitet werden
      if (polygon === true && i === (arr.length - 1) && typeof arr[i][0] === 'number'){
        continue;
      }
      arr[i] = interchangeRekursiv(arr[i], polygon);
    }
    return arr;
  }
}
