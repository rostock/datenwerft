/**
 * @function
 * @name applyFilters
 *
 * applies filters based on passed filter objects list
 *
 * @param {Object[]} filterObjectsList - filter objects list
 */
function applyFilters(filterObjectsList) {
  if (filterObjectsList.length > 0) {
    showAllGeoJsonFeatures();
    window.currMap.eachLayer(function(layer) {
      if (layer.feature)
        filterGeoJsonFeatures(filterObjectsList, layer);
    });
  } else {
    showAllGeoJsonFeatures();
  }
}

/**
 * @function
 * @name buildTooltipHtmlCleanupEventRequest
 *
 * build tooltip HTML for a CleanupEventRequest feature
 *
 * @param {Object} feature - feature
 */
function buildTooltipHtmlCleanupEventRequest(feature) {
  let html = '';
  html += '<div class="leaflet-popup-title">';
  html +=   '<strong>' + feature.properties._title + '</strong>';
  html += '</div>';
  html += '<div class="leaflet-popup-section">';
  if (feature.properties._link_request) {
    html += '<a title="Antrag ansehen oder bearbeiten" href="' + feature.properties._link_request + '"><i ' + 'class="fas fa-pen"></i> Antrag</a>';
  }
  if (feature.properties._link_event) {
    html +=  '<br>';
    html +=  '<a title="Aktionsdaten ansehen oder bearbeiten" href="' + feature.properties._link_event + '"><i ' + 'class="fas fa-pen"></i> Aktionsdaten</a>';
  }
  if (feature.properties._link_venue) {
    html +=  '<br>';
    html +=  '<a title="Treffpunkt ansehen oder bearbeiten" href="' + feature.properties._link_venue + '"><i ' + 'class="fas fa-pen"></i> Treffpunkt</a>';
  }
  if (feature.properties._link_details) {
    html +=  '<br>';
    html +=  '<a title="Detailangaben ansehen oder bearbeiten" href="' + feature.properties._link_details + '"><i ' + 'class="fas fa-pen"></i> Detailangaben</a>';
  }
  if (feature.properties._link_container) {
    html +=  '<br>';
    if (feature.properties._link_container.includes('update'))
      html +=  '<a title="Containerdaten ansehen oder bearbeiten" href="' + feature.properties._link_container + '"><i ' + 'class="fas fa-pen"></i> Container</a>';
    else
      html +=  '<a title="neue Containerdaten anlegen" href="' + feature.properties._link_container + '"><i ' + 'class="fas fa-circle-plus"></i> Container</a>';
  }
  if (feature.properties._link_container_delete) {
    html +=  '<br>';
    html +=  '<a title="Containerdaten löschen" href="' + feature.properties._link_container_delete + '"><i ' + 'class="fas fa-trash"></i> Containerdaten</a>';
  }
  if (feature.properties._link_dump) {
    html +=  '<br>';
    if (feature.properties._link_dump.includes('update'))
      html +=  '<a title="Müllablageplatz ansehen oder bearbeiten" href="' + feature.properties._link_dump + '"><i ' + 'class="fas fa-pen"></i> Müllablageplatz</a>';
    else
      html +=  '<a title="neuen Müllablageplatz anlegen" href="' + feature.properties._link_dump + '"><i ' + 'class="fas fa-circle-plus"></i> Müllablageplatz</a>';
  }
  if (feature.properties._link_dump_delete) {
    html +=  '<br>';
    html +=  '<a title="Müllablageplatz löschen" href="' + feature.properties._link_dump_delete + '"><i ' + 'class="fas fa-trash"></i> Müllablageplatz</a>';
  }
  html +=   '<table class="mt-2">';
  html +=     '<tbody>';
  jQuery.each(feature.properties, function (key, value) {
    if (!key.startsWith('_') && value) {
      html +=    '<tr>';
      html +=      '<td><strong>' + key + '</strong></td>';
      html +=      '<td><em>' + value + '</em></td>';
      html +=    '</tr>';
    }
  });
  html +=     '</tbody>';
  html +=   '</table>';
  html += '</div>';
  return html;
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
 * applies filters
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
      filterAttribute.name = $(this).attr('name').replace('requests-', '').replace(/-.*$/, '');
      filterAttribute.type = $(this).data('type');
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
 * @param {Object[]} filterObjectsList - filter objects list
 * @param {Object} layer - GeoJSON map layer
 */
function filterGeoJsonFeatures(filterObjectsList, layer) {
  let stillVisible = true
  let geoJsonFilterPropertyPrefix = '_filter_';
  for (let i = 0; i < filterObjectsList.length; i++) {
    let filterName = filterObjectsList[i].name;
    let filterType = filterObjectsList[i].type;
    let filterIntervalside = filterObjectsList[i].intervalside;
    let filterValue = filterObjectsList[i].value;
    let objectValue = layer.feature.properties[geoJsonFilterPropertyPrefix + filterName];
    // "left" interval date filter
    if (filterIntervalside === 'left') {
      if (filterType === 'date') {
        if (new Date(filterValue) > new Date(objectValue))
          stillVisible = false;
      }
    // "right" interval date filter
    } else if (filterIntervalside === 'right') {
      if (filterType === 'date') {
        if (new Date(objectValue) > new Date(filterValue))
          stillVisible = false;
      }
    } else {
      // text filter based on arrays
      if (filterType === 'array') {
        let tempStillVisible = false;
        for (let j = 0; j < filterValue.length; j++) {
          if (objectValue.toString() === filterValue[j].toString()) {
            tempStillVisible = true;
            break;
          }
        }
        if (!tempStillVisible)
          stillVisible = false;
      // text filter based on list values
      } else if (filterType === 'list') {
        if (objectValue.toString().toLowerCase() !== filterValue.toLowerCase())
          stillVisible = false;
      // ordinary text filter
      } else {
         // catch null values
         if (objectValue === null)
           objectValue = '';
         if (objectValue.toString().toLowerCase().indexOf(filterValue.toLowerCase()) === -1)
          stillVisible = false;
      }
    }
  }
  if (stillVisible) {
    // update map extent of currently filtered data
    updateCurrentlyFilteredDataVariables(layer);
  } else {
    // hide GeoJSON feature
    layer.getElement().style.display = 'none';
  }
}

/**
 * @function
 * @name filterReset
 *
 * resets filters
 */
function filterReset() {
  // hide filter alert
  $('#requests-filter-alert').hide();

  // empty all filter fields
  $('[id^=filter-input-requests]').each(function() {
    $(this).val('');
  });

  // reset map extent of currently filtered data
  window.currentRequestsFilterExtent = [];

  // show all GeoJSON features
  showAllGeoJsonFeatures();
}

/**
 * @function
 * @name showAllGeoJsonFeatures
 *
 * shows all GeoJSON features
 */
function showAllGeoJsonFeatures() {
  currMap.eachLayer(function(layer) {
    if (layer.feature)
      layer.getElement().style.display = '';
  });
}

/**
 * @function
 * @name updateCurrentlyFilteredDataVariables
 *
 * update currently filtered data based on passed GeoJSON map layer
 *
 * @param {Object} layer - GeoJSON map layer
 */
function updateCurrentlyFilteredDataVariables(layer) {
  let north = (
    (layer.feature.geometry.type === 'Point') ? layer.getLatLng().lat : layer.getBounds().getNorth()
  );
  let east = (
    (layer.feature.geometry.type === 'Point') ? layer.getLatLng().lng : layer.getBounds().getEast()
  );
  let south = (
    (layer.feature.geometry.type === 'Point') ? layer.getLatLng().lat : layer.getBounds().getSouth()
  );
  let west = (
    (layer.feature.geometry.type === 'Point') ? layer.getLatLng().lng : layer.getBounds().getWest()
  );
  if (window.currentRequestsFilterExtent.length === 0) {
    window.currentRequestsFilterExtent[0] = [];
    window.currentRequestsFilterExtent[0][0] = north;
    window.currentRequestsFilterExtent[0][1] = east;
    window.currentRequestsFilterExtent[1] = [];
    window.currentRequestsFilterExtent[1][0] = south;
    window.currentRequestsFilterExtent[1][1] = west;
  } else {
    if (window.currentRequestsFilterExtent[0][0] > north)
      window.currentRequestsFilterExtent[0][0] = north;
    if (window.currentRequestsFilterExtent[0][1] > east)
      window.currentRequestsFilterExtent[0][1] = east;
    if (window.currentRequestsFilterExtent[1][0] < south)
      window.currentRequestsFilterExtent[1][0] = south;
    if (window.currentRequestsFilterExtent[1][1] < west)
      window.currentRequestsFilterExtent[1][1] = west;
  }
}
