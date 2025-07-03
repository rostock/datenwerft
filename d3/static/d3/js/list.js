

/**
 * @function
 * @name initDataTable
 *
 * initializes data table and returns it
 *
 * @param {string} dataUrl - data URL
 * @param {string} languageUrl - language URL
 * @returns {Object} - data table
 */
function initDataTable(dataUrl, languageUrl) {

  return $('#datasets').DataTable({
    ajax: dataUrl,
    buttons: [],
    colReorder: false,
    columnDefs: [{
        'orderable': false,
        'targets': 'no-sort'
      }, {
        'searchable': false,
        'targets': 'no-search'
      }
    ],
    dom: '<Bfr<t>ilp>',
    fixedHeader: true,
    language: {
      url: languageUrl
    },
    lengthMenu: [[25, 50, -1], [25, 50, 'alle']],
    order: [[1, 'asc']],
    orderCellsTop: true,
    orderClasses: false,
    orderMulti: false,
    pageLength: 25,
    processing: true,
    searchDelay: 500,
    searching: false,
    serverSide: true,
    stateSave: true
  });
}

async function fetchMetadata(dataUrl, processId) {

  return fetch(`${dataUrl}?processId=${processId}`).then(response => response.json())
}