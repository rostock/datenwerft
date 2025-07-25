
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
    showAllMapFeatures();
    window.currMap.eachLayer(function(layer) {
      if (layer.feature) {
        filterGeoJsonFeatures(filterObjectsList, layer, false);
      } else if (layer.id === 'cluster') {
        let clusterLayer = layer;
        layer.eachLayer(function(subLayer) {
          filterGeoJsonFeatures(filterObjectsList, subLayer, true, clusterLayer);
        });
        layer.refreshClusters();
      }
    });
  } else {
    showAllMapFeatures();
  }
}

/**
 * @function
 * @name fetchGeoJsonFeatureCollection
 *
 * fetches GeoJSON feature collection for map
 *
 * @param {boolean} heavyLoad - large amounts of data expected?
 * @param {number} [limit=0] - limit for current loading step
 * @param {number} [offset=0] - offset for current loading step (= multiple ``limit``)
 * @param {string} url - map data composition URL
 */
async function fetchGeoJsonFeatureCollection(heavyLoad = false, limit = 0, offset = 0, url = window.mapDataUrl) {
  try {
    // set parameters for the current loading step if large amounts of data are expected
    if (heavyLoad) {
      url += '?limit=' + limit + '&offset=' + offset;
    }
    toggleModal(
      $('#loading-modal'),
      'Laden der Kartendaten',
      'Die Kartendaten werden (nach-)geladen.' + (heavyLoad ? ' Dies kann einen Moment dauern, da es sich insgesamt um eine sehr große Datenmenge handelt.' : ''),
      heavyLoad ? '#loading-modal-map-data' : null
    );
    const response = await fetch(url, {
      method: 'GET'
    });
    const data = await response.json();
    if (heavyLoad) {
      window.count += data.features.length;
      $('#loading-modal-map-data-count').text(window.count);
      if (window.count === window.border)
        $('#loading-modal-close').click();
    } else {
      setTimeout(function () {
        $('#loading-modal-close').click();
      }, 1000);
    }
    return data;
  } catch (error) {
    console.error(error);
  }
}

/**
 * @function
 * @name filterGeoJsonFeatures
 *
 * filters GeoJSON features based on passed filter objects list
 *
 * @param {Object[]} filterObjectsList - filter objects list
 * @param {Object} layer - GeoJSON map layer
 * @param {boolean} isSubLayer - GeoJSON map layer is part of a map cluster?
 * @param {Object} [clusterLayer=layer] - map cluster (equals GeoJSON map layer per default)
 */
function filterGeoJsonFeatures(filterObjectsList, layer, isSubLayer, clusterLayer = layer) {
  let stillVisible = true;
  for (let i = 0; i < filterObjectsList.length; i++) {
    // deadline filter
    if (filterObjectsList[i].name === 'deadline') {
      if (!(new Date(filterObjectsList[i].value) > new Date(layer.feature.properties['deadline_0'])) || !(new Date(layer.feature.properties['deadline_1']) > new Date(filterObjectsList[i].value)))
        stillVisible = false;
    // deadline year filter
    } else if (filterObjectsList[i].name === 'deadline-year') {
      if (!(new Date(filterObjectsList[i].value + '-12-31') > new Date(layer.feature.properties['deadline-year_0'])) || !(new Date(layer.feature.properties['deadline-year_1']) > new Date(filterObjectsList[i].value + '-01-01')))
        stillVisible = false;
    // "left" interval filter
    } else if (filterObjectsList[i].intervalside === 'left') {
      if (filterObjectsList[i].type === 'date') {
        if (new Date(filterObjectsList[i].value) > new Date(layer.feature.properties[filterObjectsList[i].name]))
          stillVisible = false;
      } else if (filterObjectsList[i].type === 'datetime') {
        if (new Date(filterObjectsList[i].value).valueOf() > new Date(layer.feature.properties[filterObjectsList[i].name]).valueOf())
          stillVisible = false;
      } else {
        if (filterObjectsList[i].value > layer.feature.properties[filterObjectsList[i].name])
          stillVisible = false;
      }
    // "right" interval filter
    } else if (filterObjectsList[i].intervalside === 'right') {
      if (filterObjectsList[i].type === 'date') {
        if (new Date(layer.feature.properties[filterObjectsList[i].name]) > new Date(filterObjectsList[i].value))
          stillVisible = false;
      } else if (filterObjectsList[i].type === 'datetime') {
        if (new Date(layer.feature.properties[filterObjectsList[i].name]).valueOf() > new Date(filterObjectsList[i].value).valueOf())
          stillVisible = false;
      } else {
        if (layer.feature.properties[filterObjectsList[i].name] > filterObjectsList[i].value)
          stillVisible = false;
      }
    // checkbox sets
    } else if (filterObjectsList[i].type === 'checkbox-set' && filterObjectsList[i].value.length > 0) {
      if (filterObjectsList[i].filtertype === 'additive') {
        for (let j = 0; j < filterObjectsList[i].value.length; j++) {
          if (layer.feature.properties[filterObjectsList[i].name].toLowerCase().indexOf(filterObjectsList[i].value[j].toLowerCase()) === -1)
            stillVisible = false;
        }
      } else {
        // work with auxiliary variable to do justice to the exclusive character (OR)
        let tempStillVisible = false;
        for (let k = 0; k < filterObjectsList[i].value.length; k++) {
          if (layer.feature.properties[filterObjectsList[i].name].toLowerCase().indexOf(filterObjectsList[i].value[k].toLowerCase()) !== -1) {
            tempStillVisible = true;
            break;
          }
        }
        if (!tempStillVisible)
          stillVisible = false;
      }
    } else if (filterObjectsList[i].type !== 'checkbox-set') {
      // date or datetime filter
      if (filterObjectsList[i].type === 'date' || filterObjectsList[i].type === 'datetime') {
        // negative or positive impact logic?
        if (filterObjectsList[i].logic === 'negative') {
          if (new Date(filterObjectsList[i].value).valueOf() === new Date(layer.feature.properties[filterObjectsList[i].name]).valueOf())
            stillVisible = false;
        } else {
          if (new Date(filterObjectsList[i].value).valueOf() !== new Date(layer.feature.properties[filterObjectsList[i].name]).valueOf())
            stillVisible = false;
        }
      // text filter based on list values
      } else if (filterObjectsList[i].type === 'list') {
        // negative or positive impact logic?
        if (filterObjectsList[i].logic === 'negative') {
          if (layer.feature.properties[filterObjectsList[i].name].toLowerCase().includes(filterObjectsList[i].value.toLowerCase()))
            stillVisible = false;
        } else {
          if (!layer.feature.properties[filterObjectsList[i].name].toLowerCase().includes(filterObjectsList[i].value.toLowerCase()))
            stillVisible = false;
        }
      // ordinary text filter
      } else {
         let value = filterObjectsList[i].value.toLowerCase();
        // handle decimal separator if a decimal number was entered
        if (/^([0-9]+,[0-9]+)$/.test(filterObjectsList[i].value) === true)
          value = filterObjectsList[i].value.replace(',', '.');
        // negative or positive impact logic?
        if (filterObjectsList[i].logic === 'negative') {
          if (layer.feature.properties[filterObjectsList[i].name].toLowerCase().indexOf(value) !== -1)
            stillVisible = false;
        } else {
          if (layer.feature.properties[filterObjectsList[i].name].toLowerCase().indexOf(value) === -1)
            stillVisible = false;
        }
      }
    }
  }
  // if feature is not marked for hiding and shall therefore continue to be visible...
  if (stillVisible) {
     // update variables for primary keys and map extent of currently filtered data
    window.currentFilterPrimaryKeys.push(layer.feature.properties[window.modelPrimaryKeyFieldName]);
    let north = ((layer.feature.geometry.type === 'Point') ? layer.getLatLng().lat : layer.getBounds().getNorth());
    let east = ((layer.feature.geometry.type === 'Point') ? layer.getLatLng().lng : layer.getBounds().getEast());
    let south = ((layer.feature.geometry.type === 'Point') ? layer.getLatLng().lat : layer.getBounds().getSouth());
    let west = ((layer.feature.geometry.type === 'Point') ? layer.getLatLng().lng : layer.getBounds().getWest());
    if (window.currentFilterExtent.length === 0) {
      window.currentFilterExtent[0] = [];
      window.currentFilterExtent[0][0] = north;
      window.currentFilterExtent[0][1] = east;
      window.currentFilterExtent[1] = [];
      window.currentFilterExtent[1][0] = south;
      window.currentFilterExtent[1][1] = west;
    } else {
      if (window.currentFilterExtent[0][0] > north)
        window.currentFilterExtent[0][0] = north;
      if (window.currentFilterExtent[0][1] > east)
        window.currentFilterExtent[0][1] = east;
      if (window.currentFilterExtent[1][0] < south)
        window.currentFilterExtent[1][0] = south;
      if (window.currentFilterExtent[1][1] < west)
        window.currentFilterExtent[1][1] = west;
    }
    // hide feature if it is affected by initial feature suppression...
    if (window.mapFilterHideInitial) {
      if (typeof layer.feature.properties.hide_initial !== 'undefined' && layer.feature.properties.hide_initial) {
        layer.setStyle({
          color: '#3388ff',
          fill: true,
          fillColor: '#3388ff',
          stroke: true,
          opacity: 1
        });
      }
    }
  // otherwise...
  } else {
    // hide feature
    if (isSubLayer) {
      window.removedLayers.push(layer);
      clusterLayer.removeLayer(layer);
    } else
      layer.getElement().style.display = 'none';
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
  // if feature has a link to its form page...
  if (feature.properties.link) {
    // open link when clicking on feature
    layer.on('click', function () {
      window.open(feature.properties.link, '_blank', 'noopener,noreferrer').focus();
    });
  }
  // if feature is inactive...
  if (typeof feature.properties.inaktiv !== 'undefined' && feature.properties.inaktiv) {
    // display feature differently from standard
    layer.setStyle({
      color: '#999',
      fillColor: '#999'
    });
  }
  // if feature shall be highlighted...
  if (window.highlightFlag) {
    if (typeof feature.properties.highlight !== 'undefined' && feature.properties.highlight) {
      // highlight feature
      layer.setStyle({
        color: 'red',
        fillColor: 'red'
      });
    }
  }
  // if feature is affected by initial feature suppression...
  if (window.mapFilterHideInitial) {
    if (typeof feature.properties.hide_initial !== 'undefined' && feature.properties.hide_initial)
      // hide feature
      layer.setStyle({
        fill: false,
        stroke: false,
        opacity: 0
      });
  }
  // if geometry is not point-like...
  if (window.geometryType !== 'Point')
    // set tooltip
    // (otherwise it will be set further down when loading the GeoJSON feature collection)
    layer.bindTooltip(feature.properties.tooltip);
}

/**
 * @function
 * @name showAllMapFeatures
 *
 * shows all features on the map (again)
 */
function showAllMapFeatures() {
  currMap.eachLayer(function(layer) {
    if (layer.feature) {
      layer.getElement().style.display = '';
      // if feature is affected by initial feature suppression...
      if (window.mapFilterHideInitial) {
        if (typeof layer.feature.properties.hide_initial !== 'undefined' && layer.feature.properties.hide_initial) {
          // hide feature
          layer.setStyle({
            fill: false,
            stroke: false,
            opacity: 0
          });
        }
      }
    } else if (layer.id === 'cluster') {
      layer.addLayers(window.removedLayers);
      layer.refreshClusters();
    }
  });
  window.removedLayers = [];
}