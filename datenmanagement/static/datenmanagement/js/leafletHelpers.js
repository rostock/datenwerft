/*
 * Erweiterungen von bestehenden Klassen
 */

/**
 * @function
 * @name getActiveOverlays
 *
 * Liefert Liste der aktivierten Layer im Layer-Auswahl-Button
 */
L.Control.Layers.prototype.getActiveOverlays = function () {
  let activeLayers = {};
  this._layers.forEach((layer) => {
    if (layer.overlay && this._map.hasLayer(layer.layer)) {
      window.currMap.eachLayer((lay) => {
        if (lay instanceof L.GeoJSON && lay.toGeoJSON().type === 'FeatureCollection'){
          activeLayers[layer.name] = lay;
        }
      });
    }
  });
  return activeLayers;
}




/*
 * Leaflet Hilfsfunktionen
 *
 * !!! Benötigen leaflet-geoman !!!
 */

/**
 * @function
 * @name getLayersOfType
 * Ausgabe aller Layer eines Typs.
 *
 * @param {string} type - Typ der zu suchenden Layer als String (Bsp.: "LineString").
 * @param {boolean} [withCompatible=false] - Mit kompatiblen Layern (Bsp.: `type="Point"` → Rückgabe aller `Point`-
 *                                           und `MultiPoint`-Layer)
 *
 * @returns {Array} Ein Array der Layer mit dem angegebenen Typ
 */
L.Map.prototype.getLayersOfType = function (type, withCompatible=false) {
  let result = []
  if (withCompatible === true){
    this.pm.getGeomanLayers().forEach((layer) => {
      if (layer.toGeoJSON().geometry.type.indexOf(type) > -1){
        result.push(layer);
      }
    });
  } else {
    this.pm.getGeomanLayers().forEach((layer) => {
      if (layer.toGeoJSON().geometry.type === type){
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
 * Liefert für einen gegebenen Layer alle anknüpfenden Layer vom selben Typ.
 * **Anknüpfend: **
 * - Bei Polygonen: mind. 2 gleiche Punkte
 * - Bei LineString: Anfang oder Endpunkt identisch
 *
 * @param {layer} layer - Layer für welchen die angeheftete Layer gefunden werden sollen.
 * @returns {Array} Ein Array
 */
L.Map.prototype.getAttachingLayers = function (layer) {
  let results = [];
  let coordsOfLayer = layer.toGeoJSON().geometry.coordinates;
  this.getLayersOfType(layer.toGeoJSON().geometry.type, false).forEach((l) => {
    for (let i = 0; i < coordsOfLayer.length-1; i++) {
      if (results.indexOf(l) > -1) {
        break;
      } else {
        let index = l.indexOf(coordsOfLayer[i]);
        if (index > -1 && (l[index+1] === coordsOfLayer[i-1] || l[index+1] === coordsOfLayer[i+1])){
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
 * Laden der Geometry aus Hidden-Input-Feld.
 *
 * @param {string} fieldID - ID des Input-Felds
 */
L.Map.prototype.loadGeometryFromField = function (fieldID) {
  let geojson = {
    "type": "Feature",
    "properties": {},
    "geometry": JSON.parse($(fieldID).val()),
    }
  let changeGeom = new L.geoJSON(geojson, {
    pointToLayer: function (feature, latlng) {
      // here you would difference between marker and circle
      return L.marker(latlng, {icon: redMarker});
    },
    templineStyle: {
      color: 'red',             // Farbe während des zeichnens
    },
    color: 'red',
    fillColor: 'red',
  }).addTo(this);
  this.fitBounds(changeGeom.getBounds());
  changeGeom._changeGeom = true;
  changeGeom.eachLayer((layer) => {
    layer._drawnByGeoman = true;
    if (layer instanceof L.Marker){
      layer.setZIndexOffset(1000);
    } else {
      layer.bringToFront();
    }
  });
  return this;
}


/**
 * @function
 * @name loadExternalData
 *
 * Nachladen zusätzlicher Datenthemen im aktuellen Sichtbereich
 *
 * @param {string} baseUrl - BasisUrl des Datenthemas
 * @param {layer} layer - Layer des Datenthemas
 */
L.Map.prototype.loadExternalData = function (baseUrl, layer) {
  let mapPart = this.getBounds();
  let center = this.getCenter();
  let rad = this.distance(center, mapPart['_northEast']) * 1.2; // Berechnen des Bounding-Circle
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
        // Verhindern, dass Daten doppelt auf der Karte angezeigt werden
        let exists = false;
        for (let e of layer.toGeoJSON().features){
          if (e.properties.uuid === geoJsonFeature.properties.uuid){
            exists = true;
          }
        }
        if (exists === false){
          geoJsonFeatureCollection.features.push(geoJsonFeature);
        }
      }
      layer.addData(geoJsonFeatureCollection);
      layer.pm.setOptions({
        draggable: false,
        allowEditing: false,
        allowRemoval: false,
        allowCutting: false,
        allowRotation: false
      }); // Geoman Optionen setzen
      layer._drawnByGeoman = false;
      if (layer instanceof L.Marker){
        layer.setZIndexOffset(0);
      } else {
        layer.bringToBack();
      }
    }
  ).catch(
    function(err) {
      console.log('Fetch Error: ' + err);
    }
  );
}



/**
 * @function
 * @name updateMap
 *
 * Laden der externen Datensätze, doppelte Daten löschen und 'aktive' Layer anheben
 *
 * @param map
 */
L.Map.prototype.updateMap = function (dataLayerControl) {
  let list = dataLayerControl.getActiveOverlays();
  if (this.getZoom() > this._minLayerZoom){
    for (const key in list) {
      this.loadExternalData(this._themaUrl[key], list[key]);
    }
    // 'Anheben' des Layers, welches bearbeitet wird
    this.eachLayer((layer) => {
      if (layer._drawnByGeoman === true){
        if (layer instanceof L.Marker){
          layer.setZIndexOffset(1000);
        } else {
          layer.bringToFront();
        }
      }
    });
  } else {
    this.eachLayer((layer) => {
      if (layer instanceof L.GeoJSON && layer.toGeoJSON().type === 'FeatureCollection' && !(layer._changeGeom)) {
        layer.clearLayers();
      }
    });
  };
  return this;
}





/**
 * @function
 * @name setInteractive
 *
 * Interaktivität für den Layer oder die Layer einer LayerGruppe setzen.
 *
 * @param {boolean} interactive
 */
L.Layer.prototype.setInteractive = function (interactive) {
  if (this.getLayers) {
    this.getLayers().forEach(layer => {
      layer.setInteractive(interactive);
    });
    return;
  }
  if (!this._path) {
    return;
  }

  this.options.interactive = interactive;

  if (interactive) {
    this._path.classList.add('leaflet-interactive');
  } else {
    this._path.classList.remove('leaflet-interactive');
  }
};


/**
 * @function
 * @name unite
 *
 * Bildet die Vereinigung mit einem gegebenen Layer
 *
 * @param diffrentLayer
 * @returns {*}
 */
L.Polygon.prototype.unite = function (diffrentLayer, type){
  let feature1 = this.toGeoJSON();
  let feature2 = diffrentLayer.toGeoJSON();
  if (type.indexOf('Polygon') > 0){
    // MultiPolygon
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates); // Vereinigung erzeugen
    result = interchangeRekursiv(result, true); // Lat, Lng tauschen
    this.setLatLngs(result);
  } else if (type.indexOf('Polygon') === 0){
    // Polygon
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates); // Vereinigung erzeugen
    result = interchangeRekursiv(result, true); // Lat, Lng tauschen
    if (result.length === 1){
      this.setLatLngs(result[0]);
    }
  }
}


/**
 * @function
 * @name interchangeLatLng
 *
 *
 *
 * @returns {*}
 */
L.Layer.prototype.interchangeLatLng = function () {
  let json = this.toGeoJSON();
  let polygon = false;
  let arr = json.geometry.coordinates;
  if (json.geometry.type.indexOf('Polygon') > -1){
    polygon = true;
  }
  this.toGeoJSON().geometry.coordinates = interchangeRekursiv(arr, polygon);
}

