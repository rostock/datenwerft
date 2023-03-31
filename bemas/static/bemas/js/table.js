/* global $ */
/* eslint no-undef: "error" */

/**
 * @function
 * @name determineColumnDefinitions
 *
 * determines column definitions
 *
 * @param {boolean} actionLinksColumn - column with action links present?
 * @returns {Object[]} - column definitions
 */
function determineColumnDefinitions(actionLinksColumn) {
  let columnDefs = [];
  if (actionLinksColumn) {
    columnDefs = [{
      'orderable': false,
      'targets': -1
    }];
  }
  return columnDefs;
}

/**
 * @function
 * @name initDataTable
 *
 * @param {string} dataUrl - data URL
 * @param {string} languageUrl - language URL
 * @param {boolean} actionLinksColumn - column with action links present?
 * @param {Object[]} initialOrder - initial order
 *
 * initialize data table
 */
function initDataTable(dataUrl, languageUrl, actionLinksColumn, initialOrder) {
  $('#datasets').DataTable({
    ajax: dataUrl,
    buttons: [
      {
        extend: 'csvHtml5',
        fieldSeparator: ';',
        exportOptions: {
          // no export of columns marked respectively
          columns: ':visible:not(.no-export)'
        }
      }, {
        extend: 'excelHtml5',
        title: '',
        exportOptions: {
          columns: ':visible:not(.no-export)'
        }
      }, {
        extend: 'pdfHtml5',
        exportOptions: {
          columns: ':visible:not(.no-export)'
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
    columnDefs: determineColumnDefinitions(actionLinksColumn),
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
