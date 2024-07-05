/*
 * extensions of existing Leaflet classes
 */

/**
 * @function
 * @name getActiveOverlays
 *
 * returns all active layers in layer controls
 *
 * @returns {Object} - all active layers in layer controls
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
 * Leaflet helper functions
 */

/**
 * @function
 * @name getLayersOfType
 *
 * returns all layers of passed type
 *
 * @param {string} type - type of layers to search as a string (example: 'LineString')
 * @param {boolean} [withCompatible=false] - with compatible layers? (example: return all point and multi-point layers if `type='Point'`)
 * @returns {Array} - all layers of passed type
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
 * returns all layers attached to passed layer (provided that they are of the same type),
 * where attached means:
 * - polygons: at least two points are identical
 * - lines: start or end points are identical
 *
 * @param {Object} layer - layer for which all attached layers of the same type shall be found
 * @returns {Array} - all layers attached to passed layer (provided that they are of the same type)
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
 * @name loadGeometryFromContextDict
 *
 * loads geometry from passed context dict to map
 *
 * @param {string} contextDict - context dict
 * @param {boolean} [zoomToPreviousGeometries=true] - shall only one geometry be processed at once?
 * @returns {this} - map with geometry loaded from passed input field
 */
L.Map.prototype.loadGeometryFromContextDict = function(contextDict, zoomToPreviousGeometries = true) {
  let geojson = {
    'type': 'Feature',
    'properties': {},
    'geometry': JSON.parse(contextDict.geometry),
  }
  let geojsonLayer = new L.geoJSON(geojson, {
    onEachFeature: function(feature, layer) {
      layer.bindTooltip('<strong>' + contextDict.text + '</strong>', {
        direction: 'center',
        opacity: 0.8
      });
    }
  }).addTo(this);
  if (zoomToPreviousGeometries)
    this.fitBounds(geojsonLayer.getBounds());
  // set Leaflet-Geoman options
  geojsonLayer.pm.setOptions({
    draggable: false,
    allowEditing: false,
    allowRemoval: false,
    allowCutting: false,
    allowRotation: false
  });
  geojsonLayer._drawnByGeoman = false;
  if (geojsonLayer instanceof L.Marker)
    geojsonLayer.setZIndexOffset(0);
  else
    geojsonLayer.bringToBack();
  return this;
}

/**
 * @function
 * @name loadGeometryFromField
 *
 * loads geometry from passed input field to map
 *
 * @param {string} fieldId - input field ID
 * @returns {this} - map with geometry loaded from passed input field
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
    // color while drawing
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
 * loads geometry from foreign key field target objects to map
 *
 * @param {string} url - URL for loading geometry from foreign key field target objects
 * @param {string} foreignModel - name of the target model of the foreign key
 * @param {string} fieldName - name of the foreign key field
 * @param {string} fieldTitle - title of the foreign key field
 * @param {string} [fieldValue=''] - value of the foreign key field
 * @param {string} [targetObjectPrimaryKey=''] - primary key of the foreign key's current target object
 * @param {boolean} [singleMode=true] - shall only one geometry be processed at once?
 * @returns {this} - map with geometry loaded from foreign key field target objects
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
        // define new empty GeoJSON feature
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
        // define new empty GeoJSON feature collection
        let geoJsonFeatureCollection = {
          type: 'FeatureCollection',
          features: []
        };
        for (let i = 0; i < data.object_list.length; i++) {
          let geom = data.object_list[i];
          // if geometry is not empty...
          if (geom.indexOf('EMPTY') === -1) {
            wkt.read(geom.substring(geom.indexOf(';') + 1, geom.length));
            // if geometry is not already displayed on map...
            if (data.uuids[i] !== targetObjectPrimaryKey) {
              // define new empty GeoJSON feature
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
 * reloads additional features in the current viewing area of the map
 *
 * @param {string} name - name of the data theme or the WFS feature type
 * @param {string} baseUrl - base URL of the data theme or the WFS
 * @param {Object} layer - layer of the data theme or the WFS feature type
 * @param {boolean} [isWFS=false] - is it a WFS?
 */
L.Map.prototype.loadExternalData = function(name, baseUrl, layer, isWFS = false) {
  let url = baseUrl;
  let mapPart = this.getBounds();
  if (isWFS === true) {
    let boundingBoxParameter = '&bbox=' + mapPart.getSouthEast().lat + ',' + mapPart.getSouthEast().lng + ',' + mapPart.getNorthWest().lat + ',' + mapPart.getNorthWest().lng + ',urn:ogc:def:crs:EPSG::4326';
    url += boundingBoxParameter;
  } else {
    let center = this.getCenter();
    // calculate bounding circle
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
        // define new empty GeoJSON feature collection
        let geoJsonFeatureCollection = {
          type: 'FeatureCollection',
          features: []
        };
        let wkt = new Wkt.Wkt();
        for (let i = 0; i < data.object_list.length; i++) {
          let geom = data.object_list[i];
          // if geometry is not empty...
          if (geom.indexOf('EMPTY') === -1) {
            wkt.read(geom.substring(geom.indexOf(';') + 1, geom.length));
            // define new empty GeoJSON feature
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
            // prevent data from appearing twice on the map
            let exists = false;
            for (let e of layer.toGeoJSON().features) {
              if (e.properties.uuid === geoJsonFeature.properties.uuid)
                exists = true;
            }
            if (exists === false)
              geoJsonFeatureCollection.features.push(geoJsonFeature);
          }
        }
        layer.addData(geoJsonFeatureCollection);
      }
      // set Leaflet-Geoman options
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
 * loads additional features to the map,
 * deletes duplicate features from the map (if the source of the features is a data theme),
 * and raises active layers in the map
 *
 * @param {Object} layerControl - layer control to activate additional data themes or WFS feature types
 * @param {boolean} [isWFS=false] - is it a WFS?
 * @returns {this} - modified map
 */
L.Map.prototype.updateMap = function(layerControl, isWFS = false) {
  // dermine active layers in the layer control
  let list = layerControl.getActiveOverlays();
  let minZoom = isWFS === true ? this._minLayerZoomForWFSFeaturetypes : this._minLayerZoomForDataThemes;
  // if there are any active layers at all...
  if (Object.keys(list).length > 0) {
    if (this.getZoom() > minZoom) {
      for (let key in list) {
        this.loadExternalData(key, this._themaUrl[key], list[key], isWFS);
      }
      // raise the layer being edited
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
 * sets interactivity for the passed layer or layer group
 *
 * @param {boolean} interactive - interactive?
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
 * carries out a union with a passed layer
 *
 * @param {Object} diffrentLayer - layer to perform the union with
 * @param {string} type - type of the layer to perform the union with as a string (example: 'LineString')
 */
L.Polygon.prototype.unite = function(diffrentLayer, type) {
  let feature1 = this.toGeoJSON();
  let feature2 = diffrentLayer.toGeoJSON();
  // multi-polygon...
  if (type.indexOf('Polygon') > 0) {
    // carry out union
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates);
    // swap x and y coordinates
    result = interchangeRecursive(result, true);
    this.setLatLngs(result);
  // polygon...
  } else if (type.indexOf('Polygon') === 0) {
    // carry out union
    let result = martinez.union(feature1.geometry.coordinates, feature2.geometry.coordinates);
    // swap x and y coordinates
    result = interchangeRecursive(result, true);
    if (result.length === 1)
      this.setLatLngs(result[0]);
  }
}

/**
 * @function
 * @name interchangeLatLng
 *
 * reverses the order of x and y coordinates
 */
L.Layer.prototype.interchangeLatLng = function() {
  let json = this.toGeoJSON();
  let polygon = false;
  let arr = json.geometry.coordinates;
  if (json.geometry.type.indexOf('Polygon') > -1)
    polygon = true;
  this.toGeoJSON().geometry.coordinates = interchangeRecursive(arr, polygon);
}
