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
  const response = fetch(
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
  );
  response.then(response => response.blob())
  .then(myblob => window.open(URL.createObjectURL(myblob)));
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
 * @returns {Object} - table
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
    colReorder: true,
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
      // provide highlight flag rows (= records) with with red text color
      } else if ($(row).find('.text-danger').length) {
        $(row).addClass('text-danger');
      }
    },
    dom: '<Bfr<t>ilp>',
    fixedHeader: true,
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
    serverSide: true,
    stateSave: true
  });
}
