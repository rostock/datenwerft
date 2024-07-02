/**
 * @function
 * @name applyFilters
 *
 * applies filters to requests based on passed filter objects list
 *
 * @param {Object[]} filterObjectsList - filter objects list
 */
function applyFilters(filterObjectsList) {
  if (filterObjectsList.length > 0) {
    showAllGeoJsonFeatures();
    window.currMap.eachLayer(function(layer) {
      filterGeoJsonFeatures(filterObjectsList, layer, false);
    });
  } else {
    showAllGeoJsonFeatures();
  }
}

/**
 * @function
 * @name fetchGeoJsonFeatureCollection
 *
 * fetches GeoJSON feature collection for map
 *
 * @param {string} url - map data composition URL
 */
async function fetchGeoJsonFeatureCollection(url) {
  try {
    const response = await fetch(url, {
      method: 'GET'
    });
    return await response.json();
  } catch (error) {
    console.error(error);
  }
}

/**
 * @function
 * @name filterApplication
 *
 * applies filters to requests
 */
function filterApplication() {
  // reset map extent of currently filtered data
  window.currentRequestsFilterExtent = [];

  // show filter alert
  $('#requests-filter-alert').show();

  // create filter objects list
  let filterObjectsList = [];
  $('[id^=filter-input-requests]').each(function() {
    if ($(this).val()) {
      // create filter as object with name, type, (optionally) interval side and value
      let filterAttribute = {};
      console.log($(this).attr('name'));
      filterAttribute.name = $(this).attr('name').replace('requests-', '').replace(/-$/, '');
      filterAttribute.type = $(this).data('type');
      console.log(filterAttribute.name);
      if ($(this).data('intervalside'))
        filterAttribute.intervalside = $(this).data('intervalside');
      filterAttribute.value = $(this).val();
      // add filter object to filter objects list
      filterObjectsList.push(filterAttribute);
    }
  });

  // apply filters
  applyFilters(filterObjectsList);
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
