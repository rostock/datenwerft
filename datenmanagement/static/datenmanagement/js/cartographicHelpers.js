/**
 * @function
 * @name configureLeafletGeoman
 *
 * konfiguriert Leaflet-Geoman in der übergebenen Karte
 *
 * @param {Object} map - Karte
 * @param {String} [geometryType=''] - Geometrietyp des aktuellen Datenthemas im Formular
 */
function configureLeafletGeoman(map, geometryType = '') {
  // eigene Übersetzungen definieren
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

  // Tooltip-Sprache mit eigenen Übersetzungen setzen
  map.pm.setLang('customDe', customTranslation, 'de');

  // Optionen für das Zeichnen von Objekten setzen
  map.pm.setPathOptions(map._pathOptions);

  // globale Optionen setzen
  map.pm.setGlobalOptions({
    snapDistance: 10,
    continueDrawing: false, // nach Hinzufügen einer Geometrie
    markerStyle: {
      icon: redMarker
    }
  })

  // Kontrollelemente setzen
  if (geometryType === 'Point') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,  // Kreis-Marker setzen
      drawCircle: false,        // Kreis zeichnen
      drawPolyline: false,      // Linie zeichnen
      drawRectangle: false,     // Rechteck zeichnen
      drawPolygon: false,       // Polygon zeichnen
      drawText: false,          // Text erstellen
      dragMode: false,          // Geometrie verschieben
      editMode: false,          // Stützpunkt bearbeiten
      cutPolygon: false,        // Polygon aus anderer Geometrie ausschneiden
      rotateMode: false,        // Geometrie rotieren
      removalMode: false        // Geometrie löschen
    });
  } else if (geometryType === 'LineString') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,  // Kreis-Marker setzen
      drawCircle: false,        // Kreis zeichnen
      drawMarker: false,        // Marker setzen
      drawRectangle: false,     // Rechteck zeichnen
      drawPolygon: false,       // Polygon zeichnen
      drawText: false,          // Text erstellen
      dragMode: false,          // Geometrie verschieben
      cutPolygon: false,        // Polygon aus anderer Geometrie ausschneiden
      rotateMode: false         // Geometrie rotieren
    });
  } else if (geometryType === 'Polygon') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,  // Kreis-Marker setzen
      drawCircle: false,        // Kreis zeichnen
      drawMarker: false,        // Marker setzen
      drawPolyline: false,      // Linie zeichnen
      drawText: false,          // Text erstellen
      dragMode: false,          // Geometrie verschieben
      cutPolygon: false,        // Polygon aus anderer Geometrie ausschneiden
      rotateMode: false         // Geometrie rotieren
    });
  } else if (geometryType === 'MultiPolygon') {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,  // Kreis-Marker setzen
      drawCircle: false,        // Kreis zeichnen
      drawMarker: false,        // Marker setzen
      drawPolyline: false,      // Linie zeichnen
      drawText: false,          // Text erstellen
      dragMode: false,          // Geometrie verschieben
      rotateMode: false         // Geometrie rotieren
    });
  } else {
    map.pm.addControls({
      position: 'topleft',
      drawCircleMarker: false,  // Kreis-Marker setzen
      drawCircle: false,        // Kreis zeichnen
      drawMarker: false,        // Marker setzen
      drawPolyline: false,      // Linie zeichnen
      drawRectangle: false,     // Rechteck zeichnen
      drawPolygon: false,       // Polygon zeichnen
      drawText: false,          // Text erstellen
      dragMode: false,          // Geometrie verschieben
      editMode: false,          // Stützpunkt bearbeiten
      cutPolygon: false,        // Polygon aus anderer Geometrie ausschneiden
      rotateMode: false,        // Geometrie rotieren
      removalMode: false        // Geometrie löschen
    });
  }

  // falls Geometrietyp des Datenthemas flächenhaft ist...
  if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
    // Button zum Adoptieren von Geometrien als Kontrollelement hinzufügen
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
      // Geometrien interaktiv setzen
      if (e.btnName === 'adoptGeometry' && e.button.toggleStatus === false) {
        map.getLayersOfType('Polygon', true).forEach((layer) => {
          layer.setInteractive(true);
          layer.on('click', () => {
            let j = JSON.parse($('#id_geometrie').val());
            let type = (j.type.indexOf('MultiPolygon') > -1) ? 'MultiPolygon' : 'Polygon';
            // falls bislang noch keine Geometrie vorliegt...
            if (map.pm.getGeomanDrawLayers().length < 1) {
              // Layer aus adoptierter Geometrie erzeugen
              let geometryToAdopt = new L.geoJSON(layer.toGeoJSON(), {
                color: 'red'
              });
              // erzeugten Layer und alle Sublayer zu Leaflet-Geoman-Draw-Layer hinzufügen
              geometryToAdopt._changeGeom = true;
              geometryToAdopt.eachLayer((layer) => {
                layer._drawnByGeoman = true;
              });
              // Leaflet-Geoman-Draw-Layer zur Karte hinzufügen
              geometryToAdopt.addTo(map);
            }
            map.pm.getGeomanDrawLayers()[0].unite(layer, type);
          });
        });
      }
    });
    map.on('pm:buttonclick', (e) => {
      // Bearbeitung deaktivieren
      if (e.btnName === 'adoptGeometry' && e.button.toggleStatus === true) {
        map.pm.getGeomanLayers().forEach((layer) => {
          layer.setInteractive(false);
        });
      }
    });
    map.on('pm:actionclick', (e) => {
      // Bearbeitung deaktivieren
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
 * konfiguriert die übergebene Karte
 *
 * @param {Object} map - Karte
 * @param {Object} owsProxyUrl - URL des OWS-Proxies
 * @param {Object} [additionalWmsLayers={}] - zusätzliche Karten
 */
function configureMap(map, owsProxyUrl, additionalWmsLayers = {}) {
  // Rendering der Feature-Layer auf der Karte etwas beschleunigen
  map.preferCanvas = true;

  // Standard-Zoom-Kontrollelemente entfernen und durch solche mit eigenen Tooltips ersetzen
  map.zoomControl.remove();
  L.control.zoom({
    zoomInTitle:'hineinzoomen',
    zoomOutTitle:'herauszoomen'
  }).addTo(map);

  // ORKa.MV definieren
  const orkamv = L.tileLayer('https://www.orka-mv.de/geodienste/orkamv/tiles/1.0.0/orkamv/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: 'Kartenbild © Hanse- und Universitätsstadt Rostock (<a href="https://creativecommons.org/licenses/by/4.0/deed.de" target="_blank">CC BY 4.0</a>)<br>Kartendaten © <a href="https://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> (<a href="https://opendatacommons.org/licenses/odbl/" target="_blank">ODbL</a>) und LkKfS-MV'
  });

  // ORKa.MV standardmäßig zur Karte hinzufügen
  map.addLayer(orkamv);

  // OpenStreetMap definieren
  const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap-Mitwirkende</a>'
  });

  // basemap.de definieren
  const basemapde = L.tileLayer.wms('https://sgx.geodatenzentrum.de/wms_basemapde', {
    layers: 'de_basemapde_web_raster_farbe',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© GeoBasis-DE/BKG'
  });

  // Liegenschaftskarte definieren
  const liegenschaftskarte = L.tileLayer.wms(owsProxyUrl + '/liegenschaftskarte/wms', {
    layers: 'hro.liegenschaftskarte',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    attribution: '© Hanse- und Universitätsstadt Rostock (MLV intern)'
  });

  // Luftbild definieren
  const luftbild = L.tileLayer(owsProxyUrl + '/luftbild_mv-20/tiles/1.0.0/hro.luftbild_mv-20.luftbild_mv-20/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {
    maxZoom: map._maxLayerZoom,
    attribution: '© GeoBasis-DE/M-V'
  });

  // zuvor definierte Karten als Hintergrundkarten zusammenfassen
  const baseMaps = {
    'basemap.de': basemapde,
    'Liegenschaftskarte': liegenschaftskarte,
    'Luftbild': luftbild,
    'OpenStreetMap': osm,
    'ORKa.MV': orkamv
  };

  // Kilometerquadrate ETRS89/UTM-33N definieren
  const kilometerquadrate = L.tileLayer.wms('https://geo.sv.rostock.de/geodienste/koordinatensysteme/wms', {
    layers: 'hro.koordinatensysteme.kilometerquadrate_utm',
    format: map._wmsFormat,
    maxZoom: map._maxLayerZoom,
    transparent: true
  });

  // zuvor definierte Karten als Overlay-Karten zusammenfassen
  let overlayMaps = {
    'Kilometerquadrate ETRS89/UTM-33N': kilometerquadrate
  };

  // ggf. zusätzlich definierte Karten zu den Overlay-Karten hinzufügen
  overlayMaps = Object.assign(overlayMaps, additionalWmsLayers);

  // Umschalter für Hintergrundkarten zur Karte hinzufügen
  L.control.layers(baseMaps, overlayMaps).addTo(map);

  // Kartenprojektion EPSG:25833 definieren
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
 * fügt Standortbestimmung zur übergebenen Karte hinzu
 *
 * @param {Object} map - Karte
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
 * erstellt ein HTML-Resultat aus einem Resultat der Adressensuche
 *
 * @param {string} index - Index des Resultats aus der Adressensuche
 * @param {string} uuid - UUID des Resultats aus der Adressensuche
 * @param {string} titel - Titel des Resultats aus der Adressensuche
 * @param {string} gemeindeteil_abkuerzung - Abkürzung des Gemeindeteils aus dem Resultat aus der Adressensuche
 * @returns {string} - HTML-Resultat
 */
function getAddressSearchResult(index, uuid, titel, gemeindeteil_abkuerzung) {
  let result = '<div class="result-element" data-feature="' + index + '" data-uuid="' + uuid + '"><strong>' + titel + '</strong>';
  if (gemeindeteil_abkuerzung)
    result += ' <small>(' + gemeindeteil_abkuerzung + ')</small>';
  return result;
}

/**
 * @function
 * @name initializeAddressSearch
 *
 * initialisiert die Adressensuche
 *
 * @param {Object} searchField - Sucheingabefeld der Adressensuche
 * @param {string} url - URL der Adressensuche
 * @param {string} [addressType=''] - Typ des Adressenbezugs (Adresse, Straße oder Gemeindeteil)
 * @param {Object} [addressUuidField=null] - Feld mit UUID der/des referenzierten Adresse, Straße oder Gemeindeteils
 */
function initializeAddressSearch(searchField, url, addressType = '', addressUuidField = null) {
  // bei Klick auf Stelle außerhalb der Adressensuche...
  results.click(function(e) {
    $('html').one('click',function() {
      // Resultate der Adressensuche leeren
      results.children().remove();
      results.fadeOut();
    });
    e.stopPropagation();
  });

  // ab dem dritten eingegebenen Zeichen in entsprechendem Eingabefeld Adressensuche durchführen
  searchField.keyup(function() {
    if ($(this).val().length >= 3) {
      let searchText = searchField.val();
      fetch(url + '?query=' + searchText, {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => showAddressSearchResults(data, addressType, searchField, addressUuidField))
      .catch(error => console.log(error))
    } else {
      results.children().remove();
      results.fadeOut();
    }
  });

  // bei Klick in Eingabefeld für Adressensuche dieses und die Resultate der Adressensuche leeren
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
 * setzt Konstanten für die übergebene Karte
 *
 * @param {Object} map - Karte
 */
function setMapConstants(map) {
  // allgemeine Konstanten
  map._wmsFormat = 'image/png';
  map._maxLayerZoom = 19;
  map._minLayerZoom = 13;
  map._themaUrl = {};

  // Optionen für das Zeichnen von Objekten
  map._pathOptions = {
    color: 'red', // Linienfarbe für gezeichnete Objekte
    fillColor: 'red', // Füllfarbe für gezeichnete Objekte
    requireSnapToFinish: true, // Zeichnen von Polygonen endet mit bestehendem Punkt
    templineStyle: {
      color: 'red' // Linienfarbe während des Zeichnens
    }
  };
}

/**
 * @function
 * @name setMapExtentByXYAndZoomLevel
 *
 * setzt den Kartenausschnitt mittels Kartenzentrum und Zoom-Level
 *
 * @param {number} x - x-Koordinate des Kartenzentrums
 * @param {number} y - y-Koordinate des Kartenzentrums
 * @param {number} zoomLevel - Zoom-Level
 */
function setMapExtentByXYAndZoomLevel(x, y, zoomLevel) {
  currMap.panTo([y, x]);
  currMap.setZoom(zoomLevel);
}

/**
 * @function
 * @name setMapExtentByBoundingBox
 *
 * setzt den Kartenausschnitt mittels Bounding-Box
 *
 * @param {number} min_x - minimale x-Koordinate
 * @param {number} min_y - minimale y-Koordinate
 * @param {number} max_x - maximale x-Koordinate
 * @param {number} max_y - maximale y-Koordinate
 */
function setMapExtentByBoundingBox(min_x, min_y, max_x, max_y) {
  currMap.fitBounds([[max_y, max_x], [min_y, min_x]]);
}

/**
 * @function
 * @name setMapExtentByLeafletBounds
 *
 * setzt den Kartenausschnitt mittels Leaflet-Bounding-Box-Objekt
 *
 * @param {Object} leafletBounds - Leaflet-Bounding-Box-Objekt
 */
function setMapExtentByLeafletBounds(leafletBounds) {
  currMap.fitBounds(leafletBounds);
}

/**
 * @function
 * @name showAddressSearchResults
 *
 * zeigt und behandelt die Resultate der Adressensuche
 *
 * @param {JSON} json - Resultate der Adressensuche
 * @param {string} addressType - Typ des Adressenbezugs (Adresse, Straße oder Gemeindeteil)
 * @param {Object} searchField - Sucheingabefeld der Adressensuche
 * @param {Object} addressUuidField - Feld mit UUID der/des referenzierten Adresse, Straße oder Gemeindeteils
 */
function showAddressSearchResults(json, addressType, searchField, addressUuidField) {
  // Resultate leeren
  results.children().remove();

  // JSON durchgehen...
  jQuery.each(json.features, function(index, item) {
    // je JSON-Feature ein Resultat bauen, falls JSON-Feature nicht als "historisch" markiert ist
    if (!item.properties.historisch) {
      let titel;
      if (item.properties._title_.indexOf(', ') !== -1)
        titel = item.properties._title_.substring(item.properties._title_.lastIndexOf(', ') + 2);
      else
        titel = item.properties._title_;
      let result = '';
      // falls Datenmodell Adressenbezug vorsieht...
      if (addressType !== '') {
        // nur Objektgruppen berücksichtigen, die mit dem Typ des Adressenbezugs übereinstimmen
        let substring = item.properties.objektgruppe;
        if (item.properties.objektgruppe.indexOf(' HRO') !== -1)
          substring = item.properties.objektgruppe.substring(0, item.properties.objektgruppe.lastIndexOf(' HRO'));
        if (substring === addressType) {
          result = getAddressSearchResult(index, item.properties.uuid, titel, item.properties.gemeindeteil_abkuerzung);
          result += '</div>';
        }
      // ansonsten...
      } else {
        // alle Objektgruppen berücksichtigen
        result = getAddressSearchResult(index, item.properties.uuid, titel, item.properties.gemeindeteil_abkuerzung);
        result += '<small class="text-black-50"><em>' + item.properties.objektgruppe.replace(/ HRO/, '') + '</em></small></div>';
      }
      if (result !== '')
        results.append(result);
    }
  });

  // Resultate einblenden
  results.fadeIn();

  // bei Klick auf ein Resultat...
  results.children().on('click', function() {
    // Button „Marker setzen“ aktivieren
    $('#addressToMap').prop('disabled', false);
    // falls Datenmodell Adressenbezug vorsieht...
    if (addressType !== '') {
      // Text des Resultats in Suchfeld übernehmen
      // und UUID als Data-Attribut in Feld mit UUID der/des referenzierten Adresse, Straße oder Gemeindeteils übernehmen
      let text = $(this).children('strong').text();
      if ($(this).children('small'))
        text += ' ' + $(this).children('small').text();
      searchField.val(text);
      addressUuidField.val($(this).data('uuid'));
    // ansonsten...
    } else {
      // Text des Resultats in Suchfeld übernehmen
      searchField.val($(this).children('strong').text());
    }
    // Karte auf Resultat zoomen
    window.featureGeometry = json.features[$(this).data('feature')].geometry;
    if (featureGeometry.type === 'Point') {
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
  });
}
