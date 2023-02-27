/* global $ */
/* eslint no-undef: "error" */

/**
 * @function
 * @name customMapFilters
 *
 * behandelt Ein-Klick- sowie andere individuelle Kartenfilter
 * und gibt Liste für Filterobjekte zurück
 *
 * @param {string} filterId - ID des Filters
 * @returns {Object[]} - Liste für Filterobjekte
 */
function customMapFilters(filterId) {
  // Liste für Filterobjekte definieren
  let filterList = [];

  // aktuelles Datum
  let currentDate = new Date().toJSON().slice(0, 10);

  // Ein-Klick-Filter behandeln
  switch (filterId) {
    case 'baustellen-geplant-ende-nicht-abgeschlossen':
      // Filterobjekt(e) zur Liste für Filterobjekte hinzufügen
      filterList.push(createFilter('ende', 'date', 'right', 'positive', currentDate));
      filterList.push(createFilter('status', 'list', 'both', 'negative', 'abgeschlossen'));
      break;
    case 'baustellen-geplant-beginn-nicht-imbau':
      // Filterobjekt(e) zur Liste für Filterobjekte hinzufügen
      filterList.push(createFilter('beginn', 'date', 'right', 'positive', currentDate));
      filterList.push(createFilter('ende', 'date', 'left', 'positive', currentDate));
      filterList.push(createFilter('status', 'list', 'both', 'negative', 'im Bau (P8)'));
      break;
  }

  return filterList;
}

/**
 * @function
 * @name createFilter
 *
 * erstellt ein Filterobjekt
 *
 * @param {string} name - Name
 * @param {string} type - Typ
 * @param {string} intervalside - "Intervallseite"
 * @param {string} logic - Wirkungslogik
 * @param {*} value - Wert
 * @returns {Object} - Filterobjekt
 */
function createFilter(name, type, intervalside, logic, value) {
  let filter = {};
  filter.name = name;
  filter.type = type;
  filter.intervalside = intervalside;
  filter.logic = logic;
  filter.value = value;
  return filter;
}
