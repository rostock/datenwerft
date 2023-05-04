/* global $ */
/* eslint no-undef: "error" */

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
    data = data.replaceAll(/amp;/g, '');
    // replace HTML element <br>
    data = data.replaceAll(/<br>/g, brReplacement);
    // strip all HTML elements
    data = data.replace( /(<([^>]+)>)/ig, '');
    // replace multiple whitespaces by one whitespace
    data = data.replaceAll(/ +/g, ' ');
  }
  return data.trim(); // remove any remaining whitespaces from both sides
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
 */
function initDataTable(dataUrl, languageUrl, initialOrder) {
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
    colReorder: true,
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
    lengthMenu: [[25, 50, -1], [25, 50, 'alle']],
    // initial order
    order: initialOrder,
    orderCellsTop: true,
    orderClasses: false,
    orderMulti: false,
    pageLength: 25,
    processing: true,
    searchDelay: 500,
    searching: true,
    serverSide: true,
    stateSave: true
  });
}
