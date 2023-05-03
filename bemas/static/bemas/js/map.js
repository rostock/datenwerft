/* global $, jQuery, toggleModal */
/* eslint no-undef: "error" */

/**
 * @function
 * @name fetchGeoJsonFeatureCollection
 *
 * fetches GeoJSON feature collection for map
 *
 * @param {string} url - map data composition URL
 * @param {boolean} [lastCall=false] - last function call?
 */
async function fetchGeoJsonFeatureCollection(url, lastCall=false) {
  try {
    if (!lastCall)
      toggleModal($('#loading-modal'), 'Laden der Kartendaten', 'Die Kartendaten werden (nach-)geladen.');
    const response = await fetch(url, {
      method: 'GET'
    });
    const data = await response.json();
    if (lastCall)
      toggleModal($('#loading-modal'));
    return data;
  } catch (error) {
    console.error(error);
  }
}

/**
 * @function
 * @name setGeoJsonFeaturePropertiesAndActions
 *
 * sets properties and actions for each GeoJSON feature on each GeoJSON map layer
 *
 * @param {Object} feature - GeoJSON feature
 * @param {Object} layer - GeoJSON map layer
 */
function setGeoJsonFeaturePropertiesAndActions(feature, layer) {
  let html = '';
  html += '<div class="leaflet-popup-title">';
  html +=   '<strong>' + feature.properties._title + '</strong>';
  html +=    '<a class="ms-2" href="' + feature.properties._link_update + '"><i class="fas fa-pen" title="' + feature.properties._title + ' bearbeiten"></i></a>';
  html +=    '<a class="ms-2" href="' + feature.properties._link_delete + '"><i class="fas fa-trash" title="' + feature.properties._title + ' löschen"></i></a>';
  if (feature.properties._link_events)
    html +=  '<a class="ms-2" href="' + feature.properties._link_events + '"><i class="fas fa-paperclip" title="Journalereignisse anzeigen"></i></a>';
  html +=    '<a class="ms-2" href="' + feature.properties._link_logentries + '"><i class="fas fa-clock-rotate-left" title="Einträge im Bearbeitungsverlauf anzeigen"></i></a>';
  html += '</div>';
  html += '<div class="leaflet-popup-section">';
  html +=   '<table>';
  html +=     '<tbody>';
  jQuery.each(feature.properties, function (key, value) {
    if (!key.startsWith('_') && value) {
      html +=    '<tr>';
      html +=      '<td>' + key + ':</td>';
      html +=      '<td><em>' + value + '</em></td>';
      html +=    '</tr>';
    }
  });
  html +=     '</tbody>';
  html +=   '</table>';
  html += '</div>';
  layer.bindPopup(html);
}
