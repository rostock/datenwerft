/**
 * @function
 * @name applyFilters
 *
 * applies filters for passed model based on passed filter objects list
 *
 * @param {string} model - model
 * @param {Object[]} filterObjectsList - filter objects list
 */
function applyFilters(model, filterObjectsList) {
  if (filterObjectsList.length > 0) {
    showAllGeoJsonFeatures(model);
    window.currMap.eachLayer(function(layer) {
      if (layer.feature && model.includes(layer.feature.properties._model)) {
        filterGeoJsonFeatures(model, filterObjectsList, layer, false);
      } else if (layer.id === model + 'Cluster') {
        let clusterLayer = layer;
        layer.eachLayer(function(subLayer) {
          filterGeoJsonFeatures(model, filterObjectsList, subLayer, true, clusterLayer);
        });
        layer.refreshClusters();
      }
    });
  } else {
    showAllGeoJsonFeatures(model);
  }
}

/**
 * @function
 * @name createFilterObject
 *
 * creates a filter object based on passed name, type and value, and returns it
 *
 * @param {string} name - name
 * @param {string} type - type
 * @param {*} value - value
 * @returns {Object} - filter object
 */
function createFilterObject(name, type, value) {
  let filter = {};
  filter.name = name;
  filter.type = type;
  filter.value = value;
  return filter;
}

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
    if (lastCall === false || lastCall === null)
      toggleModal($('#loading-modal'), 'Laden der Kartendaten', 'Die Kartendaten werden (nach-)geladen.');
    const response = await fetch(url, {
      method: 'GET'
    });
    const data = await response.json();
    if (lastCall === true || lastCall === null)
      toggleModal($('#loading-modal'));
    return data;
  } catch (error) {
    console.error(error);
  }
}

/**
 * @function
 * @name filterApplication
 *
 * applies filters for passed model
 *
 * @param {string} model - model
 */
function filterApplication(model) {
  // enable button to transfer currently filtered data to table
  $('#' + model + '-subsetter').prop('disabled', false);

  // reset primary keys and map extent of currently filtered data
  if (model === 'complaints') {
    window.currentComplaintsFilterPrimaryKeys = [];
    window.currentComplaintsFilterExtent = [];
    window.currentComplaintsFilterOriginatorsPrimaryKeys = [];
  } else if (model === 'originators') {
    window.currentOriginatorsFilterPrimaryKeys = [];
    window.currentOriginatorsFilterExtent = [];
  }

  // show filter alert
  $('#' + model + '-filter-alert').show();

  // create filter objects list
  let filterObjectsList = [];
  $('[id^=filter-input-' + model + ']').each(function() {
    if ($(this).val()) {
      // create filter as object with name, type, (optionally) interval side and value
      let filterAttribute = {};
      filterAttribute.name = $(this).attr('name').replace(model + '-', '').replace(/-.*$/, '');
      filterAttribute.type = $(this).data('type');
      if ($(this).data('intervalside'))
        filterAttribute.intervalside = $(this).data('intervalside');
      filterAttribute.value = $(this).val();
      // add filter object to filter objects list
      filterObjectsList.push(filterAttribute);
    }
  });

  // apply filters
  applyFilters(model, filterObjectsList);
}

/**
 * @function
 * @name filterGeoJsonFeatures
 *
 * filters GeoJSON features based on passed filter objects list
 *
 * @param {string} model - model
 * @param {Object[]} filterObjectsList - filter objects list
 * @param {Object} layer - GeoJSON map layer
 * @param {boolean} isSubLayer - GeoJSON map layer is part of a map cluster?
 * @param {Object} [clusterLayer=layer] - map cluster (equals GeoJSON map layer per default)
 */
function filterGeoJsonFeatures(model, filterObjectsList, layer, isSubLayer, clusterLayer = layer) {
  let stillVisible = true;
  for (let i = 0; i < filterObjectsList.length; i++) {
    // "left" interval date filter
    if (filterObjectsList[i].intervalside === 'left') {
      if (filterObjectsList[i].type === 'date') {
        if (new Date(filterObjectsList[i].value) > new Date(layer.feature.properties['_' + filterObjectsList[i].name + '_']))
          stillVisible = false;
      }
    // "right" interval date filter
    } else if (filterObjectsList[i].intervalside === 'right') {
      if (filterObjectsList[i].type === 'date') {
        if (new Date(layer.feature.properties['_' + filterObjectsList[i].name + '_']) > new Date(filterObjectsList[i].value))
          stillVisible = false;
      }
    } else {
      // text filter based on arrays
      if (filterObjectsList[i].type === 'array') {
        let tempStillVisible = false;
        for (let j = 0; j < filterObjectsList[i].value.length; j++) {
          if (layer.feature.properties[filterObjectsList[i].name].toString() === filterObjectsList[i].value[j].toString()) {
            tempStillVisible = true;
            break;
          }
        }
        if (!tempStillVisible)
          stillVisible = false;
      // text filter based on list values
      } else if (filterObjectsList[i].type === 'list') {
        if (layer.feature.properties['_' + filterObjectsList[i].name + '_'].toLowerCase() !== filterObjectsList[i].value.toLowerCase())
          stillVisible = false;
      // ordinary text filter
      } else {
         if (layer.feature.properties['_' + filterObjectsList[i].name + '_'].toLowerCase().indexOf(filterObjectsList[i].value.toLowerCase()) === -1)
          stillVisible = false;
      }
    }
  }
  if (stillVisible) {
    // update variables for primary keys and map extent of currently filtered data
    updateCurrentlyFilteredDataVariables(model, layer);
  } else {
    // hide GeoJSON feature
    if (isSubLayer) {
      if (model === 'complaints') {
        window.removedComplaintsLayers.push(layer);
      } else if (model === 'originators') {
        window.removedOriginatorsLayers.push(layer);
      }
      clusterLayer.removeLayer(layer);
    } else
      layer.getElement().style.display = 'none';
  }
}

/**
 * @function
 * @name filterReset
 *
 * resets filters for passed model
 *
 * @param {string} model - model
 */
function filterReset(model) {
  // disable button to transfer currently filtered data to table
  $('#' + model + '-subsetter').prop('disabled', true);

  // hide filter alert
  $('#' + model + '-filter-alert').hide();

  // empty all filter fields
  $('[id^=filter-input-' + model + ']').each(function() {
    $(this).val('');
  });

  // reset primary keys and map extent of currently filtered data
  if (model === 'complaints') {
    window.currentComplaintsFilterPrimaryKeys = [];
    window.currentComplaintsFilterExtent = [];
    window.currentComplaintsFilterOriginatorsPrimaryKeys = [];
  } else if (model === 'originators') {
    window.currentOriginatorsFilterPrimaryKeys = [];
    window.currentOriginatorsFilterExtent = [];
  }

  // show all GeoJSON features
  showAllGeoJsonFeatures(model);
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
  html +=    '<a class="ms-2" href="' + feature.properties._link_update + '"><i class="fas fa-pen" title="' + feature.properties._title + ' ansehen oder bearbeiten"></i></a>';
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

/**
 * @function
 * @name showAllGeoJsonFeatures
 *
 * shows all GeoJSON features of passed model
 *
 * @param {string} model - model
 */
function showAllGeoJsonFeatures(model) {
  currMap.eachLayer(function(layer) {
    if (layer.feature && model.includes(layer.feature.properties._model)) {
      layer.getElement().style.display = '';
    } else if (layer.id === model + 'Cluster') {
        if (model === 'complaints') {
          layer.addLayers(window.removedComplaintsLayers);
        } else if (model === 'originators') {
          layer.addLayers(window.removedOriginatorsLayers);
        }
        layer.refreshClusters();
    }
  });
  if (model === 'complaints') {
    window.removedComplaintsLayers = [];
  } else if (model === 'originators') {
    window.removedOriginatorsLayers = [];
  }
}

/**
 * @function
 * @name updateCurrentlyFilteredDataVariables
 *
 * update variables of currently filtered data for passed model based on passed GeoJSON map layer
 *
 * @param {string} model - model
 * @param {Object} layer - GeoJSON map layer
 */
function updateCurrentlyFilteredDataVariables(model, layer) {
  let y = (layer.getLatLng().lat);
  let x = (layer.getLatLng().lng);
  if (model === 'complaints') {
    window.currentComplaintsFilterPrimaryKeys.push(layer.feature.properties._pk);
    window.currentComplaintsFilterOriginatorsPrimaryKeys.push(layer.feature.properties._originator__id_);
    if (window.currentComplaintsFilterExtent.length === 0) {
      window.currentComplaintsFilterExtent[0] = [];
      window.currentComplaintsFilterExtent[0][0] = y;
      window.currentComplaintsFilterExtent[0][1] = x;
      window.currentComplaintsFilterExtent[1] = [];
      window.currentComplaintsFilterExtent[1][0] = y;
      window.currentComplaintsFilterExtent[1][1] = x;
    } else {
      if (window.currentComplaintsFilterExtent[0][0] > y)
        window.currentComplaintsFilterExtent[0][0] = y;
      if (window.currentComplaintsFilterExtent[0][1] > x)
        window.currentComplaintsFilterExtent[0][1] = x;
      if (window.currentComplaintsFilterExtent[1][0] < y)
        window.currentComplaintsFilterExtent[1][0] = y;
      if (window.currentComplaintsFilterExtent[1][1] < x)
        window.currentComplaintsFilterExtent[1][1] = x;
    }
  } else if (model === 'originators') {
    window.currentOriginatorsFilterPrimaryKeys.push(layer.feature.properties._pk);
    if (window.currentOriginatorsFilterExtent.length === 0) {
      window.currentOriginatorsFilterExtent[0] = [];
      window.currentOriginatorsFilterExtent[0][0] = y;
      window.currentOriginatorsFilterExtent[0][1] = x;
      window.currentOriginatorsFilterExtent[1] = [];
      window.currentOriginatorsFilterExtent[1][0] = y;
      window.currentOriginatorsFilterExtent[1][1] = x;
    } else {
      if (window.currentOriginatorsFilterExtent[0][0] > y)
        window.currentOriginatorsFilterExtent[0][0] = y;
      if (window.currentOriginatorsFilterExtent[0][1] > x)
        window.currentOriginatorsFilterExtent[0][1] = x;
      if (window.currentOriginatorsFilterExtent[1][0] < y)
        window.currentOriginatorsFilterExtent[1][0] = y;
      if (window.currentOriginatorsFilterExtent[1][1] < x)
        window.currentOriginatorsFilterExtent[1][1] = x;
    }
  }
}
