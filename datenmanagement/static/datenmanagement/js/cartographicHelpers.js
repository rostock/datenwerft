/**
 * @function
 * @name configureLeafletGeoman
 *
 * configures Leaflet-Geoman in passed map
 *
 * @param {Object} map - map
 * @param {string} [geometryType=''] - geometry type of the current data theme in the form
 */
function configureLeafletGeoman(map, geometryType = '') {
  // define custom translations
  const customTranslation = {
    actions: {
      cancel: 'abbrechen',
      finish: 'beenden',
      removeLastVertex: 'letzten Stützpunkt löschen'
    },
    buttonTitles: {
      cutButton: 'Teile aus vorhandenen Kartenobjekten ausschneiden',
      deleteButton: 'vorhandene Kartenobjekte löschen',
      dragButton: 'vorhandene Kartenobjekte verschieben',
      drawLineButton: 'Linie zeichnen',
      drawMarkerButton: 'Marker (neu) setzen',
      editButton: 'vorhandene Kartenobjekte bearbeiten'
    },
    tooltips: {
      continueLine: 'klicken, um weiteren Stützpunkt zu setzen',
      finishLine: 'weitere Stützpunkte setzen oder auf beliebigen Stützpunkt klicken, um Linie abzuschließen',
      finishPoly: 'weitere Stützpunkte setzen oder auf ersten Stützpunkt klicken, um Polygon abzuschließen',
      finishRect: 'klicken, um Rechteck abzuschließen',
      firstVertex: 'klicken, um ersten Stützpunkt zu setzen',
      placeMarker: 'klicken, um Marker zu setzen'
    },
  };

  // set tooltip language with custom translations
  map.pm.setLang('customDe', customTranslation, 'de');

  // set options for drawing objects
  map.pm.setPathOptions(map._pathOptions);

  // set global options
  map.pm.setGlobalOptions({
    snapDistance: 10,
    continueDrawing: false, // after adding a geometry
    markerStyle: {
      icon: redMarker
    }
  })

  // set control elements
  if (geometryType === 'Point') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,
      drawCircle: false,
      drawPolyline: false,
      drawRectangle: false,
      drawPolygon: false,
      drawText: false,
      dragMode: false,
      editMode: false,
      cutPolygon: false,
      rotateMode: false,
      removalMode: false
    });
  } else if (geometryType === 'LineString') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,
      drawCircle: false,
      drawMarker: false,
      drawRectangle: false,
      drawPolygon: false,
      drawText: false,
      dragMode: false,
      cutPolygon: false,
      rotateMode: false
    });
  } else if (geometryType === 'Polygon') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,
      drawCircle: false,
      drawMarker: false,
      drawPolyline: false,
      drawText: false,
      dragMode: false,
      cutPolygon: false,
      rotateMode: false
    });
  } else if (geometryType === 'MultiPolygon') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,
      drawCircle: false,
      drawMarker: false,
      drawPolyline: false,
      drawText: false,
      dragMode: false,
      rotateMode: false
    });
  } else {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,
      drawCircle: false,
      drawMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawPolygon: false,
      drawText: false,
      dragMode: false,
      editMode: false,
      cutPolygon: false,
      rotateMode: false,
      removalMode: false
    });
  }

  // if the geometry type of the data theme is areal...
  if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
    // add control button to adopt geometries
    map.pm.Toolbar.createCustomControl({
      name: 'adoptGeometry',
      title: 'vorhandene Geometrien adoptieren',
      block: 'edit',
      className: 'adopt-geometry-control',
      actions: [
        'finishMode'
      ]
    });
    map.on('pm:buttonclick', (e) => {
      // set geometries interactively
      if (e.btnName === 'adoptGeometry' && e.button.toggleStatus === false) {
        map.getLayersOfType('Polygon', true).forEach((layer) => {
          layer.setInteractive(true);
          layer.on('click', () => {
            let j = JSON.parse($('#id_geometrie').val());
            let type = (j.type.indexOf('MultiPolygon') > -1) ? 'MultiPolygon' : 'Polygon';
            // if no geometry is available yet...
            if (map.pm.getGeomanDrawLayers().length < 1) {
              // create layer from adopted geometry
              let geometryToAdopt = new L.geoJSON(layer.toGeoJSON(), {
                color: 'red'
              });
              // add created layer and all sublayers to Leaflet-Geoman draw layer
              geometryToAdopt._changeGeom = true;
              geometryToAdopt.eachLayer((layer) => {
                layer._drawnByGeoman = true;
              });
              // add Leaflet-Geoman draw layer to map
              geometryToAdopt.addTo(map);
            }
            map.pm.getGeomanDrawLayers()[0].unite(layer, type);
          });
        });
      }
    });
    map.on('pm:buttonclick', (e) => {
      // disable editing
      if (e.btnName === 'adoptGeometry' && e.button.toggleStatus === true) {
        map.pm.getGeomanLayers().forEach((layer) => {
          layer.setInteractive(false);
        });
      }
    });
    map.on('pm:actionclick', (e) => {
      // disable editing
      if (e.btnName === 'adoptGeometry' && e.text === 'beenden') {
        map.pm.getGeomanLayers().forEach((layer) => {
          layer.setInteractive(false);
        });
      }
    });
  }
}

/**
 * @function
 * @name configureMap
 *
 * configures the passed map
 *
 * @param {Object} map - map
 * @param {Object} owsProxyUrl - URL of OWS proxy
 * @param {Object} [additionalWmsLayers={}] - additional WMS layers
 */
function configureMap(map, owsProxyUrl, additionalWmsLayers = {}) {
  // slightly speed up the rendering of the feature layers on the map
  map.preferCanvas = true;

  // remove standard zoom controls and replace them with ones with custom tooltips
  map.zoomControl.remove();
  L.control.zoom({
    zoomInTitle:'hineinzoomen',
    zoomOutTitle:'herauszoomen'
  }).addTo(map);

  // define ORKa.MV
  const orkamv = L.tileLayer('https://www.orka-mv.de/geodienste/orkamv/tiles/1.0.0/orkamv/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: 'Kartenbild © Hanse- und Universitätsstadt Rostock (<a href="https://creativecommons.org/licenses/by/4.0/deed.de" target="_blank" rel="noopener noreferrer">CC BY 4.0</a>)<br>Kartendaten © <a href="https://www.openstreetmap.org/" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> (<a href="https://opendatacommons.org/licenses/odbl/" target="_blank" rel="noopener noreferrer">ODbL</a>) und LkKfS-MV'
  });

  // define OpenStreetMap
  const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap-Mitwirkende</a>'
  });

  // define basemap.de
  const basemapde = L.tileLayer.wms('https://sgx.geodatenzentrum.de/wms_basemapde', {
    layers: 'de_basemapde_web_raster_farbe',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© GeoBasis-DE/BKG'
  });

  // define Liegenschaftskarte
  const liegenschaftskarte = L.tileLayer.wms(owsProxyUrl + '/liegenschaftskarte/wms', {
    layers: 'hro.liegenschaftskarte',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© Hanse- und Universitätsstadt Rostock (MLV intern)'
  });

  // define Luftbild
  const luftbild = L.tileLayer('https://geo.sv.rostock.de/geodienste/luftbild_mv-20/tiles/1.0.0/hro.luftbild_mv-20.luftbild_mv-20/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: '© GeoBasis-DE/M-V'
  });

  // define Luftbild 2021
  const luftbild_2021 = L.tileLayer.wms(owsProxyUrl + '/luftbild_2021/wms', {
    layers: 'hro.luftbild_2021.luftbild_2021',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© Hanse- und Universitätsstadt Rostock (MLV intern)'
  });

  // define Luftbild 2022
  const luftbild_2022 = L.tileLayer.wms(owsProxyUrl + '/luftbild_2022/wms', {
    layers: 'hro.luftbild_2022.luftbild_2022',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© GeoBasis-DE/M-V'
  });

  // combine previously defined maps as background maps
  // and add default map
  let baseMaps;
  if (map._highZoomMode === true) {
    // set basemap.de as default map
    map.addLayer(basemapde);
    baseMaps = {
      'basemap.de': basemapde,
      'Liegenschaftskarte': liegenschaftskarte,
      'Luftbild 2021 (6 cm)': luftbild_2021,
      'Luftbild 2022 (10 cm)': luftbild_2022
    };
  } else {
    // set ORKa.MV as default map
    map.addLayer(orkamv);
    baseMaps = {
      'basemap.de': basemapde,
      'Liegenschaftskarte': liegenschaftskarte,
      'Luftbild': luftbild,
      'OpenStreetMap': osm,
      'ORKa.MV': orkamv
    };
  }

  // define Kilometerquadrate ETRS89/UTM-33N
  const kilometerquadrate = L.tileLayer.wms('https://geo.sv.rostock.de/geodienste/koordinatensysteme/wms', {
    layers: 'hro.koordinatensysteme.kilometerquadrate_utm',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    transparent: true
  });

  // combine previously defined maps as overlay maps
  let overlayMaps = {
    'Kilometerquadrate ETRS89/UTM-33N': kilometerquadrate
  };

  // if necessary, add additional WMS layers to the overlay maps as well
  overlayMaps = Object.assign(additionalWmsLayers, overlayMaps);

  // add background map toggle to map
  L.control.layers(baseMaps, overlayMaps).addTo(map);

  // define map projection
  proj4.defs([
    [
      'EPSG:25833',
      '+proj=utm +zone=33 +ellps=WGS84 +towgs84=0,0,0,0,0,0,1 +units=m +no_defs'
    ],
  ]);
}

/**
 * @function
 * @name enableMapLocate
 *
 * adds location control to the passed map
 *
 * @param {Object} map - map
 */
function enableMapLocate(map) {
  L.control.locate({
    drawCircle: false,
    drawMarker: false,
    flyTo: true,
    locateOptions: {
      enableHighAccuracy: true
    },
    setView: 'untilPan',
    strings: {
      title: 'Standortbestimmung'
    }
  }).addTo(map);
}

/**
 * @function
 * @name getAddressSearchResult
 *
 * creates an HTML result from an address search result and returns it
 *
 * @param {string} index - index of the address search result
 * @param {string} uuid - UUID of the address search result
 * @param {string} titel - title of the address search result
 * @param {string} gemeindeteil_abkuerzung - district abbreviation of the address search result
 * @returns {string} - HTML result
 */
function getAddressSearchResult(index, uuid, titel, gemeindeteil_abkuerzung) {
  let result = '<div class="result-element" data-feature="' + index + '" data-uuid="' + uuid + '"><strong>' + titel + '</strong>';
  if (gemeindeteil_abkuerzung && (typeof window.addressSearchLongResults === 'undefined' || window.addressSearchLongResults === false))
    result += ' <small>(' + gemeindeteil_abkuerzung + ')</small>';
  return result;
}

/**
 * @function
 * @name initializeAddressSearch
 *
 * initializes the address search
 *
 * @param {Object} searchField - search input field of the address search
 * @param {string} url - URL of the address search
 * @param {string} [addressType=''] - address reference type (i.e. address, street or district)
 * @param {Object} [addressUuidField=null] - field with UUID of referenced address, street or district
 * @param {Object} [searchClass='address_hro'] - address search class
 */
function initializeAddressSearch(searchField, url, addressType = '', addressUuidField = null, searchClass = 'address_hro') {
  // clicking on a location outside of the address search...
  results.click(function(e) {
    $('html').one('click',function() {
      // clearing address search results
      results.children().remove();
      results.fadeOut();
    });
    e.stopPropagation();
  });

  // carry out an address search from the third character entered in the corresponding input field
  searchField.keyup(function() {
    if ($(this).val().length >= 3) {
      let searchText = searchField.val();
      fetch(url + '?class=' + searchClass + '&query=' + searchText, {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => showAddressSearchResults(data, addressType, searchField, addressUuidField, searchClass))
      .catch(error => console.log(error))
    } else {
      results.children().remove();
      results.fadeOut();
    }
  });

  // on clicking in the input field for address search:
  // empty it and the results of the address search as well
  searchField.on('click', function() {
    $(this).val('');
    if (addressUuidField !== null)
      addressUuidField.val('');
    $('#results-container').hide();
  });
}

/**
 * @function
 * @name setMapConstants
 *
 * sets constants for the passed map
 *
 * @param {Object} map - map
 * @param {number} maxLayerZoom - maximum map layer zoom
 * @param {boolean} [highZoomMode=false] - map in high zoom mode?
 */
function setMapConstants(map, maxLayerZoom, highZoomMode = false) {
  // global constants
  map._wfsDefaultParameters = '?service=WFS&version=2.0.0&request=GetFeature&typeNames=TYPENAMES&outputFormat=GeoJSON&srsName=urn:ogc:def:crs:EPSG::4326';
  map._wmsFormat = 'image/png';
  map._highZoomMode = highZoomMode;
  map._maxLayerZoom = maxLayerZoom;
  if (highZoomMode === true)
    (maxLayerZoom + 2 > 21) ? map._maxLayerZoom = maxLayerZoom + 2 : map._maxLayerZoom = 21;
  map._minLayerZoomForWFSFeaturetypes = 16;
  map._minLayerZoomForDataThemes = 13;
  map._themaUrl = {};

  // options for drawing objects
  map._pathOptions = {
    color: 'red', // line color for drawn objects
    fillColor: 'red', // fill color for drawn objects
    requireSnapToFinish: true, // drawing polygons ends with existing point
    templineStyle: {
      color: 'red' // line color while drawing
    }
  };
}

/**
 * @function
 * @name setMapExtentByXYAndZoomLevel
 *
 * sets the map section using the passed map center and zoom level
 *
 * @param {number} x - x coordinate of the map center
 * @param {number} y - y coordinate of the map center
 * @param {number} zoomLevel - zoom level
 */
function setMapExtentByXYAndZoomLevel(x, y, zoomLevel) {
  currMap.panTo([y, x]);
  currMap.setZoom(zoomLevel);
}

/**
 * @function
 * @name setMapExtentByBoundingBox
 *
 * sets the map section using the passed bounding box
 *
 * @param {number} min_x - minimum x coordinate
 * @param {number} min_y - minimum y coordinate
 * @param {number} max_x - maximum x coordinate
 * @param {number} max_y - maximum y coordinate
 */
function setMapExtentByBoundingBox(min_x, min_y, max_x, max_y) {
  currMap.fitBounds([[max_y, max_x], [min_y, min_x]]);
}

/**
 * @function
 * @name setMapExtentByLeafletBounds
 *
 * sets the map section using the passed Leaflet bounding box object
 *
 * @param {Object} leafletBounds - Leaflet bounding box object
 */
function setMapExtentByLeafletBounds(leafletBounds) {
  currMap.fitBounds(leafletBounds);
}

/**
 * @function
 * @name showAddressSearchResults
 *
 * shows and handles the results of the address search
 *
 * @param {JSON} json - results of the address search
 * @param {string} addressType - address reference type (i.e. address, street or district)
 * @param {Object} searchField - search input field of the address search
 * @param {Object} addressUuidField - field with UUID of referenced address, street or district
 * @param {Object} searchClass - address search class
 */
function showAddressSearchResults(json, addressType, searchField, addressUuidField, searchClass) {
  // empty results
  results.children().remove();

  // go through JSON...
  jQuery.each(json.features, function(index, item) {
    // build one result for each JSON feature if the JSON feature is not marked as "historical"
    if (!item.properties.historisch) {
      let titel;
      if (item.properties._title_.indexOf(', ') !== -1)
        titel = item.properties._title_.substring(item.properties._title_.lastIndexOf(', ') + 2);
      else
        titel = item.properties._title_;
      if (typeof window.addressSearchLongResults !== 'undefined' && window.addressSearchLongResults === true) {
        let gemeinde = '';
        if (searchClass !== 'address_hro') {
          if (item.properties.gemeinde_name.indexOf(',') !== -1)
            gemeinde = item.properties.gemeinde_name.substring(0, item.properties.gemeinde_name.indexOf(','));
          else
            gemeinde = item.properties.gemeinde_name;
          gemeinde += ', ';
        }
        let appendix = '';
        if (addressType === 'Adresse')
          appendix = ', ' + item.properties.postleitzahl;
        titel = gemeinde + item.properties.gemeindeteil_name + ', ' + titel + appendix;
      }
      let result = '';
      // if model provides address reference...
      if (addressType !== '') {
        // consider object groups only that match the address reference type
        let substring = item.properties.objektgruppe;
        if (item.properties.objektgruppe.indexOf(' HRO') !== -1)
          substring = item.properties.objektgruppe.substring(0, item.properties.objektgruppe.lastIndexOf(' HRO'));
        if (substring === addressType) {
          result = getAddressSearchResult(index, item.properties.uuid, titel, item.properties.gemeindeteil_abkuerzung);
          result += '</div>';
        }
      // otherwise...
      } else {
        // consider all object groups
        result = getAddressSearchResult(index, item.properties.uuid, titel, item.properties.gemeindeteil_abkuerzung);
        result += '<small class="text-secondary"><em>' + item.properties.objektgruppe.replace(/ HRO/, '') + '</em></small></div>';
      }
      if (result !== '')
        results.append(result);
    }
  });

  // show results
  results.fadeIn();

  // clicking on a result...
  results.children().on('click', function() {
    // activate button „Marker setzen“
    $('#addressToMap').prop('disabled', false);
    // if model provides address reference...
    if (addressType !== '') {
      // copy the text of the result into the search field
      // and adopt the UUID as a data attribute in the field with UUID
      // of referenced address, street or district
      let text = $(this).children('strong').text();
      if ($(this).children('small'))
        text += ' ' + $(this).children('small').text();
      searchField.val(text);
      if (addressUuidField)
        addressUuidField.val($(this).data('uuid'));
    // otherwise...
    } else {
      // copy the text of the result into the search field
      searchField.val($(this).children('strong').text());
    }
    // zoom map to result (only if there is a map at all, though)
    if (typeof currMap !== 'undefined') {
      let resultingFeatureGeometry = json.features[$(this).data('feature')].geometry;
      if (resultingFeatureGeometry.type === 'Point') {
        resultingFeatureGeometry.coordinates = proj4('EPSG:25833', 'EPSG:4326', resultingFeatureGeometry.coordinates);
        window.featureGeometry = resultingFeatureGeometry;
        currMap.fitBounds([
          [
            featureGeometry.coordinates[1],
            featureGeometry.coordinates[0]
          ],
          [
            featureGeometry.coordinates[1],
            featureGeometry.coordinates[0]
          ]
        ]);
      } else {
        for (let i = 0; i < resultingFeatureGeometry.coordinates[0].length; i++) {
          resultingFeatureGeometry.coordinates[0][i] = proj4('EPSG:25833', 'EPSG:4326', resultingFeatureGeometry.coordinates[0][i]);
        }
        window.featureGeometry = resultingFeatureGeometry;
        currMap.fitBounds([
          [
            featureGeometry.coordinates[0][0][1],
            featureGeometry.coordinates[0][1][0]
          ],
          [
            featureGeometry.coordinates[0][2][1],
            featureGeometry.coordinates[0][0][0]
          ]
        ]);
      }
    }
  });
}
