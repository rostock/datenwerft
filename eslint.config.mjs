import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
});

export default [
  ...compat.extends("eslint:recommended"), {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.jquery,
        activateMapLayer: true,
        addField: true,
        applyFilters: true,
        bootstrap: true,
        buildTooltipHtmlCleanupEventRequest: true,
        cleanField: true,
        configureLeafletGeoman: true,
        configureMap: true,
        createFilterObject: true,
        currMap: true,
        customMapFilters: true,
        disableActionsControls: true,
        enableActionsControls: true,
        enableAddressReferenceButton: true,
        enableMapLocate: true,
        featureGeometry: true,
        fetchGeoJsonFeatureCollection: true,
        fetchPdf: true,
        filterApplication: true,
        filterReset: true,
        getFeatureCenter: true,
        getFeatureGeometryLatLng: true,
        grayMarker: true,
        initDataTable: true,
        initializeAddressSearch: true,
        interchangeRecursive: true,
        keepDjangoRequiredMessages: true,
        L: true,
        martinez: true,
        objectsExtent: true,
        orangeMarker: true,
        proj4: true,
        Promise: true,
        redMarker: true,
        reloadDataTable: true,
        results: true,
        searchField: true,
        setAddressToMarkerAddress: true,
        setButtonsPosition: true,
        setGeoJsonFeaturePropertiesAndActions: true,
        setMapConstants: true,
        setMapExtentByXYAndZoomLevel: true,
        setMapExtentByBoundingBox: true,
        setMapExtentByLeafletBounds: true,
        setMarkerToAddressSearchResult: true,
        showAllMapFeatures: true,
        subsetting: true,
        toggleModal: true,
        Wkt: true
      },
      ecmaVersion: "latest",
      sourceType: "module"
    },
    rules: {
      "no-unused-vars": ["off"]
    }
  }
];
