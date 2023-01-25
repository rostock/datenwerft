/* global $, grayMarker, interchangeRecursive, L, martinez, orangeMarker, redMarker, toggleModal, Wkt */
/* eslint no-undef: "error" */

/*
 * Erweiterungen bestehender Leaflet-Klassen
 */

/**
 * @function
 * @name getActiveOverlays
 *
 * gibt alle aktiven Layer im Layer-Control zurück
 *
 * @returns {Object} - alle aktiven Layer im Layer-Control
 */
L.Control.Layers.prototype.getActiveOverlays = function() {
  let activeLayers = {};
  this._layers.forEach((layer) => {
    if (layer.overlay && this._map.hasLayer(layer.layer)) {
      window.currMap.eachLayer((lay) => {
        if (
            lay instanceof L.GeoJSON
            && lay.toGeoJSON().type === 'FeatureCollection'
            && lay.name === layer.name
        )
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
      return L.marker(latlng, {
        icon: redMarker
      });
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
 * @name loadGeometryFromForeignKeyFieldObjects
 *
 * lädt Geometrie(n) des/der Zielobjekts/Zielobjekte eines Fremdschlüsselfeldes in Karte
 *
 * @param {string} url - URL zum Laden der Geometrie(n) des/der Zielobjekts/Zielobjekte eines Fremdschlüssels
 * @param {string} foreignModel - Name des Zieldatenmodells des Fremdschlüssels
 * @param {string} fieldName - Name des Feldes mit dem Fremdschlüssel
 * @param {string} fieldTitle - Titel des Feldes mit dem Fremdschlüssel
 * @param {string} [fieldValue=''] - Wert des Feldes mit dem Fremdschlüssel
 * @param {string} [targetObjectPrimaryKey=''] - Primärschlüssel des aktuellen Zielobjekts des Fremdschlüssels
 * @param {boolean} [singleMode=true] - Soll nur eine Geometrie verarbeitet werden?
 *
 * @returns {this} modifizierte Karte
 */
L.Map.prototype.loadGeometryFromForeignKeyFieldObjects = function(url, foreignModel, fieldName, fieldTitle, fieldValue = '', targetObjectPrimaryKey = '', singleMode = true) {
  fetch(
    String(url)
  ).then(
    (response) => {
      return response.json();
    }
  ).then(
    (data) => {
      let wkt = new Wkt.Wkt();
      let features;
      if (singleMode) {
        let geom = data.geometry;
        wkt.read(geom.substring(geom.indexOf(';') + 1, geom.length));
        // neues leeres GeoJSON-Feature definieren
        let geoJsonFeature = {
          type: 'Feature',
          geometry: null,
          properties: {
            'uuid': data.uuid,
            'datenthema': data.model_name,
            'foreignkey': foreignModel
          },
          crs: {
            type: 'name',
            properties: {
              'name': 'urn:ogc:def:crs:EPSG::4326'
            }
          }
        };
        geoJsonFeature.geometry = wkt.toJson();
        features = geoJsonFeature;
      } else {
        // neue leere GeoJSON-FeatureCollection definieren
        let geoJsonFeatureCollection = {
          type: 'FeatureCollection',
          features: []
        };
        for (let i = 0; i < data.object_list.length; i++) {
          let item = data.object_list[i];
          wkt.read(item.substring(item.indexOf(';') + 1, item.length));
          // falls Geometrie nicht bereits auf der Karte angezeigt wird...
          if (data.uuids[i] !== targetObjectPrimaryKey) {
            // neues leeres GeoJSON-Feature definieren
            let geoJsonFeature = {
              type: 'Feature',
              geometry: null,
              properties: {
                'uuid': data.uuids[i],
                'datenthema': data.model_name,
                'foreignkey': foreignModel
              },
              crs: {
                type: 'name',
                properties: {
                  'name': 'urn:ogc:def:crs:EPSG::4326'
                }
              }
            };
            geoJsonFeature.geometry = wkt.toJson();
            geoJsonFeatureCollection.features.push(geoJsonFeature);
          }
        }
        features = geoJsonFeatureCollection;
      }
      let foreignKeyLayer = new L.geoJSON(features, {
        pointToLayer: function (feature, latlng) {
          return new L.Marker(latlng, {
            icon: singleMode ? orangeMarker : grayMarker
          });
        },
        color: singleMode ? 'orange' : 'gray',
        fillColor: singleMode ? 'orange' : 'gray',
        onEachFeature: function (feature, layer) {
          let tooltip = singleMode ? 'aktuell ausgewählt: ' + fieldTitle + ' ' + fieldValue : 'klicken, um ' + fieldTitle + ' auszuwählen';
          layer.bindTooltip(tooltip);
          if (!singleMode)
            layer.on('click', function () {
              $('select[name=' + fieldName + ']').val(feature.properties.uuid).trigger('change');
            });
        }
      });
      foreignKeyLayer.addTo(this);
      foreignKeyLayer.eachLayer((layer) => {
        if (layer instanceof L.Marker)
          layer.setZIndexOffset(999);
        else
          layer.bringToFront();
      });
    }
  ).catch(
    (error) => {
      console.error(error);
    }
  );
  return this;
}

/**
 * @function
 * @name loadExternalData
 *
 * lädt zusätzliche Features im aktuellen Sichtbereich nach
 *
 * @param {string} name - Name des Datenthemas oder WFS-Feature-Types
 * @param {string} baseUrl - Basis-URL des Datenthemas oder WFS
 * @param {Object} layer - Layer des Datenthemas oder WFS-Feature-Types
 * @param {boolean} [isWFS=false] - Handelt es sich um einen WFS?
 */
L.Map.prototype.loadExternalData = function(name, baseUrl, layer, isWFS = false) {
  let url = baseUrl;
  let mapPart = this.getBounds();
  if (isWFS === true) {
    let boundingBoxParameter = '&bbox=' + mapPart.getSouthEast().lat + ',' + mapPart.getSouthEast().lng + ',' + mapPart.getNorthWest().lat + ',' + mapPart.getNorthWest().lng + ',urn:ogc:def:crs:EPSG::4326';
    url += boundingBoxParameter;
  } else {
    let center = this.getCenter();
    // Bounding-Circle berechnen
    let rad = this.distance(center, mapPart['_northEast']) * 1.2;
    url += '?lat=' +  center['lat'] + '&lng=' + center['lng'] + '&rad=' + rad;
  }
  fetch(
    String(url)
  ).then(
    (response) => response.json()
  ).then(
    (data) => {
      if (isWFS === true) {
        if (name === layer.name)
          layer.clearLayers();
        layer.addData(data);
      } else {
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
              'datenthema': data.model_name
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
      }
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
 * lädt zusätzliche Features in Karte,
 * löscht doppelte Features aus Karte (falls die Quelle der Features ein Datenthema ist)
 * und hebt aktive Layer in der Karte an
 *
 * @param {Object} layerControl - Layer-Control zum Zuschalten zusätzlicher Datenthemen oder WFS-Feature-Types
 * @param {boolean} [isWFS=false] - Handelt es sich um einen WFS?
 *
 * @returns {this} modifizierte Karte
 */
L.Map.prototype.updateMap = function(layerControl, isWFS = false) {
  // aktive Layer im Layer-Control ermitteln
  let list = layerControl.getActiveOverlays();
  let minZoom = isWFS === true ? this._minLayerZoomForWFSFeaturetypes : this._minLayerZoomForDataThemes;
  // falls überhaupt aktive Layer vorhanden sind...
  if (Object.keys(list).length > 0) {
    if (this.getZoom() > minZoom) {
      for (let key in list) {
        this.loadExternalData(key, this._themaUrl[key], list[key], isWFS);
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
      let zoomDifference = minZoom - this.getZoom() + 1;
      zoomDifference += zoomDifference === 1 ? ' Stufe' : ' Stufen';
      if (isWFS === true && window.showWFSZoomModal === true) {
        toggleModal(
          $('#error-modal'),
          'Sichtbarkeit zusätzlicher WFS-Feature-Types',
          'Sie müssen zunächst ' + zoomDifference + ' in die Karte hineinzoomen, bevor die zusätzlichen WFS-Feature-Types wieder sichtbar werden!'
        );
        window.showWFSZoomModal = false;
      }
      if (isWFS === false && window.showDataThemesZoomModal === true) {
        toggleModal(
          $('#error-modal'),
          'Sichtbarkeit zusätzlicher Datenthemen',
          'Sie müssen zunächst ' + zoomDifference + ' in die Karte hineinzoomen, bevor die zusätzlichen Datenthemen wieder sichtbar werden!'
        );
        window.showDataThemesZoomModal = false;
      }
      this.eachLayer((layer) => {
        if (
            layer instanceof L.GeoJSON
            && layer.toGeoJSON().type === 'FeatureCollection'
            && !(layer._changeGeom)
        )
          layer.clearLayers();
      });
    }
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
