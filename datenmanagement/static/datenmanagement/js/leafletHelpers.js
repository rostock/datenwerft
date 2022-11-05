/*
 * Erweiterungen bestehender Leaflet-Klassen
 */

/**
 * @function
 * @name getActiveOverlays
 *
 * gibt alle via Layer-Auswahl aktivierte Layer zurück
 *
 * @returns {Object} - alle via Layer-Auswahl aktivierten Layer
 */
L.Control.Layers.prototype.getActiveOverlays = function() {
  let activeLayers = {};
  this._layers.forEach((layer) => {
    if (layer.overlay && this._map.hasLayer(layer.layer)) {
      window.currMap.eachLayer((lay) => {
        if (lay instanceof L.GeoJSON && lay.toGeoJSON().type === 'FeatureCollection')
          activeLayers[layer.name] = lay;
      });
    }
  });
  return activeLayers;
}


/*
 * Leaflet-Hilfsfunktionen
 */

/**
 * @function
 * @name getLayersOfType
 *
 * gibt alle Layer des übergebenen Typs zurück
 *
 * @param {string} type - Typ der zu suchenden Layer als String (Beispiel: 'LineString')
 * @param {boolean} [withCompatible=false] - mit kompatiblen Layern? (Beispiel: bei `type='Point'` Rückgabe aller Point- und Multi-Point-Layer)
 *
 * @returns {Array} - alle Layer des übergebenen Typs
 */
L.Map.prototype.getLayersOfType = function(type, withCompatible = false) {
  let result = []
  if (withCompatible === true) {
    this.pm.getGeomanLayers().forEach((layer) => {
      if (layer.toGeoJSON().geometry.type.indexOf(type) > -1) {
        result.push(layer);
      }
    });
  } else {
    this.pm.getGeomanLayers().forEach((layer) => {
      if (layer.toGeoJSON().geometry.type === type) {
        result.push(layer);
      }
    });
  }
  return result;
}

/**
 * @function
 * @name getAttachingLayers
 *
 * gibt für einen übergebenen Layer alle anknüpfenden Layer desselben Typs zurück:
 * - anknüpfend bei Polygonen: mindestens zwei Punkte identisch
 * - anknüpfend bei Linien: Start- oder Endpunkt identisch
 *
 * @param {Object} layer - Layer, für den die anknüpfenden Layer desselben Typs gefunden werden sollen
 *
 * @returns {Array} - alle an den übergebenen Layer anknüpfenden Layer desselben Typs
 */
L.Map.prototype.getAttachingLayers = function(layer) {
  let results = [];
  let coordsOfLayer = layer.toGeoJSON().geometry.coordinates;
  this.getLayersOfType(layer.toGeoJSON().geometry.type, false).forEach((l) => {
    for (let i = 0; i < coordsOfLayer.length - 1; i++) {
      if (results.indexOf(l) > -1) {
        break;
      } else {
        let index = l.indexOf(coordsOfLayer[i]);
        if (index > -1 && (l[index + 1] === coordsOfLayer[i - 1] || l[index + 1] === coordsOfLayer[i + 1])) {
          results.push(l);
        }
      }
    }
  });
  return results;
}

/**
 * @function
 * @name loadGeometryFromField
 *
 * lädt Geometrie aus Input-Feld in Karte
 *
 * @param {string} fieldId - ID des Input-Felds
 *
 * @returns {this} modifizierte Karte
 */
L.Map.prototype.loadGeometryFromField = function(fieldId) {
  let geojson = {
    'type': 'Feature',
    'properties': {},
    'geometry': JSON.parse($(fieldId).val()),
  }
  let changeGeom = new L.geoJSON(geojson, {
    pointToLayer: function (feature, latlng) {
      return L.marker(latlng, {icon: redMarker});
    },
    // Farbe während des Zeichnens
    templineStyle: {
      color: 'red',
    },
    color: 'red',
    fillColor: 'red',
  }).addTo(this);
  this.fitBounds(changeGeom.getBounds());
  changeGeom._changeGeom = true;
  changeGeom.eachLayer((layer) => {
    layer._drawnByGeoman = true;
    if (layer instanceof L.Marker)
      layer.setZIndexOffset(1000);
    else
      layer.bringToFront();
  });
  return this;
}

/**
 * @function
 * @name loadExternalData
 *
 * lädt zusätzliche Daten im aktuellen Sichtbereich nach
 *
 * @param {string} baseUrl - Basis-URL des Datenthemas
 * @param {Object} layer - Layer des Datenthemas
 */
L.Map.prototype.loadExternalData = function(baseUrl, layer) {
  let mapPart = this.getBounds();
  let center = this.getCenter();
  // Bounding-Circle berechnen
  let rad = this.distance(center, mapPart['_northEast']) * 1.2;
  let protocol = window.location.protocol;
  let host = window.location.host;
  fetch(
    String(protocol + '//' + host + baseUrl + '?lat=' +  center['lat'] + '&lng=' + center['lng'] + '&rad=' + rad)
  ).then(
    (response) => response.json()
  ).then(
    (data) => {
      // neue leere GeoJSON-FeatureCollection definieren
      let geoJsonFeatureCollection = {
        type: 'FeatureCollection',
        features: []
      };
      let wkt = new Wkt.Wkt();
      for (let i = 0; i < data.object_list.length; i++) {
        let item = data.object_list[i];
        wkt.read(item.substring(item.indexOf(';') + 1, item.length));
        // neues leeres GeoJSON-Feature definieren
        let geoJsonFeature = {
          type: 'Feature',
          geometry: null,
          properties: {
            'uuid': data.uuids[i],
            'datenthema': data.model_name,
          },
          crs: {
            type: 'name',
            properties: {
              'name': 'urn:ogc:def:crs:EPSG::4326'
            }
          }
        };
        geoJsonFeature.geometry = wkt.toJson();
        // verhindern, dass Daten doppelt auf der Karte angezeigt werden
        let exists = false;
        for (let e of layer.toGeoJSON().features) {
          if (e.properties.uuid === geoJsonFeature.properties.uuid)
            exists = true;
        }
        if (exists === false)
          geoJsonFeatureCollection.features.push(geoJsonFeature);
      }
      layer.addData(geoJsonFeatureCollection);
      // Leaflet-Geoman-Optionen setzen
      layer.pm.setOptions({
        draggable: false,
        allowEditing: false,
        allowRemoval: false,
        allowCutting: false,
        allowRotation: false
      });
      layer._drawnByGeoman = false;
      if (layer instanceof L.Marker)
        layer.setZIndexOffset(0);
      else
        layer.bringToBack();
    }
  ).catch(
    function(error) {
      console.log(error);
    }
  );
}

/**
 * @function
 * @name updateMap
 *
 * lädt externe Datensätze in Karte, löscht doppelte Daten aus Karte und hebt aktive Layer in Karte an
 *
 * @param {Object} dataLayerControl - Layer-Control-Button zum Laden externer Datensätze
 *
 * @returns {this} modifizierte Karte
 */
L.Map.prototype.updateMap = function(dataLayerControl) {
  let list = dataLayerControl.getActiveOverlays();
  if (this.getZoom() > this._minLayerZoom) {
    for (const key in list) {
      this.loadExternalData(this._themaUrl[key], list[key]);
    }
    // anheben des Layers, der bearbeitet wird
    this.eachLayer((layer) => {
      if (layer._drawnByGeoman === true) {
        if (layer instanceof L.Marker)
          layer.setZIndexOffset(1000);
        else
          layer.bringToFront();
      }
    });
  } else {
    this.eachLayer((layer) => {
      if (layer instanceof L.GeoJSON && layer.toGeoJSON().type === 'FeatureCollection' && !(layer._changeGeom))
        layer.clearLayers();
    });
  }
  return this;
}

/**
 * @function
 * @name setInteractive
 *
 * setzt Interaktivität für den übergebenen Layer bzw. die übergebene Layer-Gruppe
 *
 * @param {boolean} interactive - interaktiv?
 */
L.Layer.prototype.setInteractive = function(interactive) {
  if (this.getLayers) {
    this.getLayers().forEach(layer => {
      layer.setInteractive(interactive);
    });
    return;
  }
  if (!this._path)
    return;
  this.options.interactive = interactive;
  if (interactive)
    this._path.classList.add('leaflet-interactive');
  else
    this._path.classList.remove('leaflet-interactive');
};

/**
 * @function
 * @name unite
 *
 * bildet die Vereinigung mit einem übergebenen Layer
 *
 * @param {Object} diffrentLayer - Layer, mit dem die Vereinigung durchgeführt werden soll
 * @param {string} type - Typ des Layer, mit dem die Vereinigung durchgeführt werden soll, als String (Beispiel: 'LineString')
 */
L.Polygon.prototype.unite = function(diffrentLayer, type) {
  let feature1 = this.toGeoJSON();
  let feature2 = diffrentLayer.toGeoJSON();
  // Multi-Polygon...
  if (type.indexOf('Polygon') > 0) {
    // Vereinigung durchführen
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates);
    // x- und y-Koordinate tauschen
    result = interchangeRecursive(result, true);
    this.setLatLngs(result);
  // Polygon...
  } else if (type.indexOf('Polygon') === 0) {
    // Vereinigung durchführen
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates);
    // x- und y-Koordinate tauschen
    result = interchangeRecursive(result, true);
    if (result.length === 1)
      this.setLatLngs(result[0]);
  }
}

/**
 * @function
 * @name interchangeLatLng
 *
 * Umkehren der Reihenfolge von x- und y-Koordinaten
 */
L.Layer.prototype.interchangeLatLng = function() {
  let json = this.toGeoJSON();
  let polygon = false;
  let arr = json.geometry.coordinates;
  if (json.geometry.type.indexOf('Polygon') > -1)
    polygon = true;
  this.toGeoJSON().geometry.coordinates = interchangeRecursive(arr, polygon);
}
