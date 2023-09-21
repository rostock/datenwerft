/**
 * @function
 * @name customMapFilters
 *
 * handles one-click filters (as well as other custom filters)
 * and returns a list with filter objects
 *
 * @param {string} filterId - filter ID
 * @returns {Object[]} - list with filter objects
 */
function customMapFilters(filterId) {
  // define list with filter objects
  let filterList = [];

  // get current date
  let currentDate = new Date().toJSON().slice(0, 10);

  // handle one-click filters
  switch (filterId) {
    case 'baustellen-geplant-ende-nicht-abgeschlossen':
      // add filter objects to defined list with filter objects
      filterList.push(createFilter('ende', 'date', 'right', 'positive', currentDate));
      filterList.push(createFilter('status', 'list', 'both', 'negative', 'abgeschlossen'));
      break;
    case 'baustellen-geplant-beginn-nicht-imbau':
      // add filter objects to defined list with filter objects
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
 * creates a filter object based on the passed parameters and returns it
 *
 * @param {string} name - name
 * @param {string} type - type
 * @param {string} intervalside - interval side
 * @param {string} logic - effect logic
 * @param {*} value - value
 * @returns {Object} - filter object
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
