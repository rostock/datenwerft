/**
 * @function
 * @name disableActionsControls
 *
 * disables action controls
 *
 */
function disableActionsControls() {
  $('#action-count').text('kein Datensatz ausgewählt');
  $('#action-select').prop('selectedIndex', 0);
  $('#action-select').prop('disabled', true);
  $('#action-button').prop('disabled', true);
}

/**
 * @function
 * @name downloadFile
 *
 * download a file
 *
 * @param {Blob} file - file
 * @param {string} [fileName='file'] - file name
 */
function downloadFile(file, fileName = 'file') {
  let href = URL.createObjectURL(file);
  let a = Object.assign(document.createElement('a'), {
    href,
    style: 'display:none',
    download: fileName
  });
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(href);
  a.remove();
}

/**
 * @function
 * @name enableActionsControls
 *
 * enables action controls
 *
 */
function enableActionsControls() {
  $('#action-select').prop('disabled', false);
  $('#action-button').prop('disabled', false);
}

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
 * @name fetchPdf
 *
 * fetches PDF file
 *
 * @param {string} url - URL
 * @param {string} csrfToken - CSRF token
 * @param {string} host - host
 */
function fetchPdf(url, csrfToken, host){
  let fileName = '';
  fetch(
    url, {
      method: 'POST',
      headers: {
        contentType: 'application/json',
        'X-CSRFToken': csrfToken
      },
      redirect: 'follow',
      origin: host,
      referrerPolicy: 'no-referrer',
      body: JSON.stringify(window.renderParams)
    }
  )
  .then(response => {
    fileName = response.headers.get('Content-Disposition').split('filename=')[1];
    return response.blob();
  })
  .then(file => downloadFile(file, fileName));
}

/**
 * @function
 * @name initDataTable
 *
 * initializes data table and returns it
 *
 * @param {string} dataUrl - data URL
 * @param {string} languageUrl - language URL
 * @param {number} numberOfColumns - number of columns
 * @returns {Object} - data table
 */
function initDataTable(dataUrl, languageUrl, numberOfColumns) {
  return $('#datasets').DataTable({
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
    createdRow: function(row) {
      // provide inactive rows (= records) with a weaker text color
      if ($(row).find('td:nth-child(2)').text() === 'nein') {
        $(row).addClass('text-secondary');
      // provide highlight flag rows (= records) with red text color
      } else if ($(row).find('.text-danger').length) {
        $(row).addClass('text-danger');
      }
    },
    dom: '<Bfr<t>ilp>',
    fixedHeader: true,
    initComplete: function() {
      this.api().columns().every(function() {
        let column = this;
        let columnFilterModeSelect = $('select.column-filter-mode', this.footer());
        let columnFilterInput = $('input.column-filter-input', this.footer());
        // listen on events of column filter input fields
        columnFilterInput.on('keyup change clear search', function() {
          let columnFilterMode = columnFilterModeSelect.val();
          // positive column filter
          if (columnFilterMode === 'P') {
            column.search(this.value).draw();
          // negative column filter
          } else {
            column.search('!' + this.value).draw();
          }
        });
        let columnFilterSelect = $('select.column-filter-select', this.footer());
        // listen on events of column filter select fields
        columnFilterSelect.on('change', function() {
          let columnFilterMode = columnFilterModeSelect.val();
          // positive column filter
          if (columnFilterMode === 'P') {
            column.search($(this).val()).draw();
          // negative column filter
          } else {
            column.search('!' + $(this).val()).draw();
          }
        });
        // listen on events of column filter mode select fields
        columnFilterModeSelect.on('change', function() {
          // trigger event of column filter input field if column filter input field exists
          if (columnFilterInput.length !== 0)
            columnFilterInput.trigger('change');
          // trigger event of column filter select field if column filter select field exists
          if (columnFilterSelect.length !== 0)
            columnFilterSelect.trigger('change');
        });
      });
    },
    language: {
      url: languageUrl
    },
    lengthMenu: [[25, 50, -1], [25, 50, 'alle']],
    order: [[numberOfColumns > 1 ? 1 : 0, 'asc']],
    orderCellsTop: true,
    orderClasses: false,
    orderMulti: false,
    pageLength: 25,
    processing: true,
    searchDelay: 500,
    searching: true,
    serverSide: true
  });
}

/**
 * @function
 * @name reloadDataTable
 *
 * reloads data table and disables action controls
 *
 * @param {Object} dataTable - data table
 */
function reloadDataTable(dataTable) {
  setTimeout(function() {
    dataTable.ajax.reload();
    disableActionsControls();
  }, 1000);
}
