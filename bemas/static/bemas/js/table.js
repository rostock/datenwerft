/**
 * @function
 * @name formatData
 *
 * formats data for export
 *
 * @param {string} data - data
 * @param {string} brReplacement - replacement character for HTML element <br>
 * @returns {string} - data for export
 */
function formatData(data, brReplacement) {
  if (data) {
    data = String(data).replaceAll(/amp;/g, '');
    // replace HTML element <br>
    data = String(data).replaceAll(/<br>/g, brReplacement);
    // strip all HTML elements
    data = String(data).replace( /(<([^>]+)>)/ig, '');
    // replace multiple whitespaces by one whitespace
    data = String(data).replaceAll(/ +/g, ' ');
  }
  return String(data).trim(); // remove any remaining whitespaces from both sides
}

/**
 * @function
 * @name initDataTable
 *
 * initializes data table
 *
 * @param {string} dataUrl - data URL
 * @param {string} languageUrl - language URL
 * @param {Object[]} initialOrder - initial order
 * @param {number} [initialPageLength=25] - initial page length
 */
function initDataTable(dataUrl, languageUrl, initialOrder, initialPageLength = 25) {
  $('#datasets').DataTable({
    ajax: dataUrl,
    buttons: [
      {
        extend: 'csvHtml5',
        fieldSeparator: ';',
        exportOptions: {
          columns: ':visible:not(.no-export)',
          format: {
            body: function (data) {
              return formatData(data, ', ' );
            }
          }
        }
      }, {
        extend: 'excelHtml5',
        title: '',
        exportOptions: {
          columns: ':visible:not(.no-export)',
          format: {
            body: function (data) {
              return formatData(data, ', ' );
            }
          }
        }
      }, {
        extend: 'pdfHtml5',
        exportOptions: {
          columns: ':visible:not(.no-export)',
          format: {
            body: function (data) {
              return formatData(data, '\n' );
            }
          }
        },
        orientation: 'landscape',
        pageSize: 'A4',
        customize: function(doc) {
          doc.defaultStyle.fontSize = 7;
          doc.pageMargins = [20, 20, 20, 20];
          doc.styles.tableHeader.fontSize = 7;
        }
      }
    ],
    colReorder: false,
    columnDefs: [{
      'orderable': false,
      'targets': 'no-sort'
    }, {
      'searchable': false,
      'targets': 'no-search'
    }],
    dom: '<Bfr<t>ilp>',
    fixedHeader: true,
    language: {
      url: languageUrl
    },
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, 'alle']],
    order: initialOrder,
    orderCellsTop: true,
    orderClasses: false,
    orderMulti: false,
    pageLength: initialPageLength,
    processing: true,
    searchDelay: 500,
    searching: true,
    serverSide: true,
    stateSave: true
  });
}
