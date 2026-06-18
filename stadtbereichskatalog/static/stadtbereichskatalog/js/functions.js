/**
 * @file functions.js
 *
 * contains (helper) functions
 */

/**
 * clears passed dropdown
 *
 * @function
 * @name clearDropdown
 *
 * @param {object} $dropdown - jQuery dropdown element
 */
function clearDropdown($dropdown) {
  $dropdown.empty();
  $dropdown.append(
    $('<option>', {
      value: '',
      text: '---------'
    })
  );
  disableFormElement($dropdown);
}


/**
 * disables passed form element
 *
 * @function
 * @name disableFormElement
 *
 * @param {object} $formElement - jQuery form element
 */
function disableFormElement($formElement) {
  $formElement.prop('disabled', true);
}


/**
 * enables passed form element
 *
 * @function
 * @name enableFormElement
 *
 * @param {object} $formElement - jQuery form element
 */
function enableFormElement($formElement) {
  $formElement.prop('disabled', false);
}


/**
 * populates passed dropdown with passed values
 *
 * @function
 * @name populateDropdown
 *
 * @param {object} $dropdown - jQuery dropdown element
 * @param {Array<string>} values - values
 */
function populateDropdown($dropdown, values) {
  $.each(values, function (index, value) {
    $dropdown.append(
      $('<option>', {
        value: value,
        text: value
      })
    );
  });
  enableFormElement($dropdown);
}


/**
 * resets table select dropdown
 *
 * @function
 * @name resetTableSelect
 */
function resetTableSelect() {
  clearDropdown($('#table-select'));
}


/**
 * populates table select dropdown with passed table names
 *
 * @function
 * @name populateTableSelect
 *
 * @param {Array<string>} tables - table names
 */
function populateTableSelect(tables) {
  populateDropdown($('#table-select'), tables);
}


/**
 * clears columns table
 *
 * @function
 * @name clearColumnsTable
 */
function clearColumnsTable() {
  $('#columns-table').empty();
}


/**
 * renders columns table by means of passed column metadata
 *
 * @function
 * @name renderColumnsTable
 *
 * @param {Array<object>} columns - column metadata
 */
function renderColumnsTable(columns) {
  let tableStructure = `
    <thead>
      <tr>
        <th>Spaltenname</th>
        <th>Datentyp</th>
        <th>Pflicht?</th>
        <th>Flags</th>
      </tr>
    </thead>
    <tbody class="table-group-divider">
    </tbody>
  `;
  $('#columns-table').append(tableStructure);
  const $columnsBody = $('#columns-table tbody');
  $.each(columns, function (index, col) {
    let flags = [];
    if (col.required) {
      flags.push('REQUIRED');
    }
    if (col.primary_key) {
      flags.push('PK');
    }
    const row = `
      <tr>
        <td class="${col.required ? 'required' : ''}">
          ${col.name}
        </td>
        <td>
          ${col.type}
        </td>
        <td>
          ${col.required ? 'ja' : 'nein'}
        </td>
        <td class="${col.primary_key ? 'pk' : ''}">
          ${flags.join(', ')}
        </td>
      </tr>
    `;
    $columnsBody.append(row);
  });
}


/**
 * clears mapping table
 *
 * @function
 * @name clearMappingTable
 */
function clearMappingTable() {
  $('#mapping-table').empty();
}


/**
 * normalizes passed string value for auto-matching
 *
 * @function
 * @name normalize
 *
 * @param {string} value - string value
 *
 * @returns {string}
 */
function normalize(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}


/**
 * validates passed preview value against passed database type
 *
 * @function
 * @name validatePreviewValue
 *
 * @param {string} dbType - database type
 * @param {string} value - preview value
 *
 * @returns {string|null}
 */
function validatePreviewValue(dbType, value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  dbType = dbType.toLowerCase();

  /*
   * integer
   */
  if (dbType.includes('integer') && !/^-?\d+$/.test(value)) {
    return 'Datentyp Quellspalte passt nicht zu Datentyp Zielspalte';
  }

  /*
   * numeric
   */
  if (dbType.includes('numeric') && isNaN(value)) {
    return 'Datentyp Quellspalte passt nicht zu Datentyp Zielspalte';
  }

  return null;
}


/**
 * validates mappings
 *
 * @function
 * @name validateMappings
 */
function validateMappings() {
  const usedHeaders = {};

  $('.mapping-select').each(function () {
    const $select = $(this);
    const selectedHeader = $select.val();
    const $row = $select.closest('tr');
    const dbType = $row.find('.db-type').text();
    const isRequired = $row.find('.db-required').text().trim() === 'ja';
    const $validationCell = $row.find('.validation-cell');
    $validationCell.empty();
    $row.removeClass('table-danger table-warning');

    /*
     * required field validation
     */
    if (
      isRequired &&
      !selectedHeader
    ) {
      $validationCell.html(
        '<div class="alert alert-danger" role="alert">' +
          `<i class="fa-solid ${ICON_ERROR}"></i>` +
          ' Pflichtzielspalte nicht gemappt' +
        '</div>'
      );
      $row.addClass('table-danger');
      return;
    }

    /*
     * duplicate mapping validation
     */
    if (selectedHeader) {
      if (!usedHeaders[selectedHeader]) {
        usedHeaders[selectedHeader] = [];
      }
      usedHeaders[selectedHeader].push($row);
    }

    /*
     * (simple) type validation
     */
    if (
      selectedHeader &&
      currentPreviewRows.length
    ) {
      const value = currentPreviewRows[0][selectedHeader];
      const typeWarning = validatePreviewValue(dbType, value);
      if (typeWarning) {
        $validationCell.html(
          `<div class="alert alert-warning" role="alert">` +
            `<i class="fa-solid ${ICON_WARNING}"></i>` +
            ` ${typeWarning}` +
          `</div>`
        );
        $row.addClass('table-warning');
      } else {
        $validationCell.html(
          '<div class="alert alert-success" role="alert">' +
            `<i class="fa-solid ${ICON_SUCCESS}"></i>` +
            ' Mapping ok' +
          '</div>'
        );
        $row.addClass('table-success');
      }
    }
  });

  /*
   * duplicate detection
   */
  for (const header in usedHeaders) {
    if (usedHeaders[header].length > 1) {
      usedHeaders[header].forEach(function ($row) {
        // only if no other (i.e. more relevant) warnings are already present
        if (!$row.hasClass('table-warning')) {
          $row.find('.validation-cell').html(
            '<div class="alert alert-warning" role="alert">' +
              `<i class="fa-solid ${ICON_WARNING}"></i>` +
              ' Quellspalte mehrfach ausgewählt' +
            '</div>'
          );
          $row.addClass('table-warning');
        }
      });
    }
  }
}


/**
 * finds matching header in uploaded file for passed database column
 *
 * @function
 * @name autoMatchColumn
 *
 * @param {string} column - database column
 *
 * @returns {string|null}
 */
function autoMatchColumn(column) {
  for (const header of currentCsvHeaders) {
    if (normalize(header) === normalize(column)) {
      return header;
    }
  }
  return null;
}


/**
 * renders mapping table
 *
 * @function
 * @name renderMappingTable
 */
function renderMappingTable() {
  let tableStructure = `
    <thead>
      <tr>
        <th>Zielspalte</th>
        <th>Datentyp</th>
        <th>Pflicht?</th>
        <th>Quellspalte</th>
        <th>Datenvorschau</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody class="table-group-divider">
    </tbody>
  `;
  $('#mapping-table').append(tableStructure);
  const $tbody = $('#mapping-table tbody');
  $tbody.empty();
  $.each(currentColumns, function(index, col) {
    let options = '<option value="">---------</option>';
    $.each(currentCsvHeaders, function (i, header) {
      const selected =
        normalize(header) === normalize(col.name)
          ? 'selected'
          : '';
      options += `
        <option value="${header}" ${selected}>
          ${header}
        </option>
      `;
    });
    const selectedHeader = autoMatchColumn(col.name);
    const previewValue =
      (
        selectedHeader &&
        currentPreviewRows.length
      )
        ? currentPreviewRows[0][selectedHeader] || ''
        : '';
    const row = `
      <tr data-db-column="${col.name}">
        <td class="${col.required ? 'required' : ''}">
          ${col.name}
        </td>
        <td class="db-type">
          ${col.type}
        </td>
        <td class="db-required">
          ${col.required ? 'ja' : 'nein'}
        </td>
        <td>
          <select class="form-select mapping-select" data-db-column="${col.name}">
            ${options}
          </select>
        </td>
        <td class="preview-cell">
          ${previewValue}
        </td>
        <td class="validation-cell">
        </td>
      </tr>
    `;
    $tbody.append(row);
  });
  validateMappings();
}


/**
 * disables upload input and button
 *
 * @function
 * @name disableUpload
 */
function disableUpload() {
  disableFormElement($('#file-input'));
  disableFormElement($('#upload-file'));
}


/**
 * enables upload input and button
 *
 * @function
 * @name enableUpload
 */
function enableUpload() {
  enableFormElement($('#file-input'));
  enableFormElement($('#upload-file'));
}


/**
 * updates preview cell for mapping row according to passed select element
 *
 * @function
 * @name updatePreview
 *
 * @param {object} $select - jQuery select element
 */
function updatePreview($select) {
  const selectedHeader = $select.val();
  const $row = $select.closest('tr');
  let previewValue = '';
  if (selectedHeader && currentPreviewRows.length) {
    previewValue = currentPreviewRows[0][selectedHeader] || '';
  }
  $row.find('.preview-cell').text(previewValue);
}


/**
 * disables import button
 *
 * @function
 * @name disableImport
 */
function disableImport() {
  disableFormElement($('#import'));
}


/**
 * enables import button
 *
 * @function
 * @name enableImport
 */
function enableImport() {
  enableFormElement($('#import'));
}


/**
 * collects mapping configuration
 *
 * @function
 * @name collectMappings
 *
 * @returns {object}
 */
function collectMappings() {
  const mappings = {};
  $('.mapping-select').each(function () {
    const targetColumn = $(this).data('db-column');
    const sourceColumn = $(this).val();
    if (sourceColumn) {
      mappings[targetColumn] = sourceColumn;
    }
  });
  return mappings;
}


/**
 * renders passed import result
 *
 * @function
 * @name renderImportResult
 *
 * @param {object} result - import result
 */
function renderImportResult(result) {
  let title, body;
  if (result && result.success) {
    title = `<i class="fa-solid ${ICON_SUCCESS} text-success"></i> Import erfolgreich`;
    body = `Es wurde(n) ${result.inserted_rows} Zeile(n) erfolgreich importiert.`;
  } else {
    title = `<i class="fa-solid ${ICON_ERROR} text-danger"></i> Import fehlgeschlagen`;
    if (result.errors) {
      if (result.errors.length > 1) {
        body = 'Beim Einlesen der Quelldatei sind Fehler aufgetreten:';
        body += '<br><br>';
        result.errors.forEach(function (error) {
          body += '<p>';
          body += `Zeile ${error.row}:`;
          body += '<br>';
          body += `Zielspalte <span class="font-monospace">${error.target_column}</span>, `;
          body += `Quellspalte <span class="font-monospace">${error.source_column}</span>, `;
          body += `Datentyp Zielspalte <span class="font-monospace">${error.target_type}</span>, `;
          body += `Fehlertyp <span class="font-monospace">${error.error_type}</span>, `;
          body += `Fehlermeldung <span class="font-monospace">${error.message}</span>, `;
          body += '</p>';
        });
      } else {
        body = 'Beim Importieren ist ein Datenbankfehler aufgetreten:';
        body += '<br><br>';
        body += `<p class="font-monospace">${result.errors[0].message}</p>`;
      }
    } else {
      body = 'Beim Importieren ist ein Fehler aufgetreten.';
    }
  }
  setModal($('#messages-modal'), title, body);
  $('#messages-modal').modal('show');
}


/**
 * disables export buttons
 *
 * @function
 * @name disableExport
 */
function disableExport() {
  $('.export-button').each(function() {
    disableFormElement($(this));
  });
}


/**
 * enables export buttons
 *
 * @function
 * @name enableExport
 */
function enableExport() {
  $('.export-button').each(function() {
    enableFormElement($(this));
  });
}


/**
 * resets year select dropdown
 *
 * @function
 * @name resetYearSelect
 */
function resetYearSelect() {
  clearDropdown($('#year-select'));
}


/**
 * populates year select dropdown with passed years
 *
 * @function
 * @name populateYearSelect
 *
 * @param {Array<string>} years - years
 */
function populateYearSelect(years) {
  populateDropdown($('#year-select'), years);
}


/**
 * resets area select dropdown
 *
 * @function
 * @name resetAreaSelect
 */
function resetAreaSelect() {
  clearDropdown($('#area-select'));
}


/**
 * populates area select dropdown with passed areas
 *
 * @function
 * @name populateAreaSelect
 *
 * @param {Array<string>} areas - areas
 */
function populateAreaSelect(areas) {
  const $areaSelect = $('#area-select');
  $.each(areas, function (index, area) {
    let text = area.code + ' – ' + area.name;
    $areaSelect.append(
      $('<option>', {
        value: area.code,
        text: text
      })
    );
  });
  enableFormElement($areaSelect);
}


/**
 * resets election select dropdown
 *
 * @function
 * @name resetElectionSelect
 */
function resetElectionSelect() {
  clearDropdown($('#election-select'));
}


/**
 * populates election select dropdown with passed elections
 *
 * @function
 * @name populateElectionSelect
 *
 * @param {Array<string>} elections - elections
 */
function populateElectionSelect(elections) {
  const $electionSelect = $('#election-select');
  $.each(elections, function (index, election) {
    let value = election.election + '__' + election.year;
    let text = election.name + ' ' + election.year;
    $electionSelect.append(
      $('<option>', {
        value: value,
        text: text
      })
    );
  });
  enableFormElement($electionSelect);
}


/**
 * builds data export URL upon passed base URL
 *
 * @function
 * @name buildDataExportURL
 *
 * @param {string} baseURL - base URL
 *
 * @returns {string}
 */
function buildDataExportURL(baseURL) {
  const schema = $('#schema-select').val();
  const table = $('#table-select').val();
  const year = $('#year-select').val();
  const area = $('#area-select').val();
  const election = $('#election-select').val();
  return `${baseURL}?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}&year=${encodeURIComponent(year)}&area=${encodeURIComponent(area)}&election=${encodeURIComponent(election)}`;
}


/**
 * shows data export modal
 *
 * @function
 * @name showDataExportModal
 *
 * @param {string} fileType - file type
 */
function showDataExportModal(fileType) {
  let title = `<i class="fa-solid ${ICON_SUCCESS} text-success"></i> Export erfolgreich`;
  let body = `Im Hintergrund wurde eine ${fileType} erzeugt und direkt von Ihrem Browser heruntergeladen, sodass diese sich nunmehr im eingestellten Download-Ordner befindet.`;
  setModal($('#messages-modal'), title, body);
  $('#messages-modal').modal('show');
}


/**
 * disables deletion button
 *
 * @function
 * @name disableDeletion
 */
function disableDeletion() {
  disableFormElement($('#deletion'));
}


/**
 * enables deletion button
 *
 * @function
 * @name enableDeletion
 */
function enableDeletion() {
  enableFormElement($('#deletion'));
}


/**
 * renders passed deletion result
 *
 * @function
 * @name renderDeletionResult
 *
 * @param {object} result - deletion result
 */
function renderDeletionResult(result) {
  let title, body;
  if (result && result.success) {
    title = `<i class="fa-solid ${ICON_SUCCESS} text-success"></i> Löschung erfolgreich`;
    body = `Es wurde(n) ${result.deleted_rows} Zeile(n) erfolgreich gelöscht.`;
  } else {
    title = `<i class="fa-solid ${ICON_ERROR} text-danger"></i> Löschung fehlgeschlagen`;
    if (result.errors) {
      body = 'Beim Löschen ist ein Datenbankfehler aufgetreten:';
      body += '<br><br>';
      body += `<p class="font-monospace">${result.errors[0].message}</p>`;
    } else {
      body = 'Beim Löschen ist ein Fehler aufgetreten.';
    }
  }
  setModal($('#messages-modal'), title, body);
  $('#messages-modal').modal('show');
}


/**
 * disables data loading button
 *
 * @function
 * @name disableDataLoading
 */
function disableDataLoading() {
  disableFormElement($('#load-data'));
}


/**
 * enables data loading button
 *
 * @function
 * @name enableDataLoading
 */
function enableDataLoading() {
  enableFormElement($('#load-data'));
}


/**
 * clears data editing table
 *
 * @function
 * @name clearEditingTable
 */
function clearEditingTable() {
  $('#editing-table').empty();
}


/**
 * extracts primary key of passed row accordings to passed column metadata and returns it
 *
 * @function
 * @name extractPrimaryKey
 *
 * @param {Array<object>} columns - column metadata
 * @param {Array<object>} row - row data
 *
 * @returns {object}
 */
function extractPrimaryKey(columns, row) {
  const pk = {};
  primaryKeyColumns.forEach(function(columnName) {
    pk[columnName] = row[columnName];
  });
  return pk;
}


/**
 * renders data editing table by means of passed column metadata and passed data
 *
 * @function
 * @name renderEditingTable
 *
 * @param {Array<object>} columns - column metadata
 * @param {Array<object>} rows - rows data
 */
function renderEditingTable(columns, rows) {
  /*
   * basic table structure
   */
  let tableStructure = `
    <thead>
      <tr>
      </tr>
    </thead>
    <tbody class="table-group-divider">
    </tbody>
  `;
  $('#editing-table').append(tableStructure);

  /*
   * columns header row
   */
  const $columnsHeader = $('#editing-table thead tr');
  columnMetadata = {};
  $.each(columns, function (index, column) {
    const columnHeader = `
      <th>
        ${column.name}
      </th>
    `;
    $columnsHeader.append(columnHeader);
    columnMetadata[column.name] = column;
  });
  $columnsHeader.append('<th><em>Redaktion</em></th>');

  /*
   * data rows
   */
  const $columnsBody = $('#editing-table tbody');
  const rowsHtml = [];
  $.each(rows, function (index, row) {
    const primaryKey = extractPrimaryKey(columns, row);
    let rowHtml = '<tr>';
    $.each(row, function (key, value) {
      let inputType, cellHtml;
      if (columnMetadata[key].type === 'integer' || columnMetadata[key].type === 'numeric') {
        inputType = 'number';
      } else {
        inputType = 'text';
      }
      if (columnMetadata[key].primary_key) {
        cellHtml = `
          <td>
            ${value}
          </td>
        `;
      } else {
        cellHtml = `
          <td>
            <input type="${inputType}" class="form-control edit-cell" data-column="${key}" value="${value ?? ''}">
          </td>
        `;
      }
      rowHtml += cellHtml;
    });
    const updateRowButtonCellHtml = `
      <td>
        <button type="button" class="btn btn-sm btn-warning update-row" disabled><i class="fa-solid ${ICON_SAVE}"></i></button>
      </td>
    `;
    rowHtml += updateRowButtonCellHtml;
    rowHtml += '</tr>';
    rowsHtml.push(rowHtml);
  });
  $columnsBody.html(rowsHtml.join(''));
  $('#editing-table tbody tr').each(function(index) {
    $(this)
      .attr('data-pk', JSON.stringify(extractPrimaryKey(columns, rows[index])))
      .attr('data-original', JSON.stringify(rows[index]));
  });
}


/**
 * detects changes in table rows and returns them
 *
 * @function
 * @name detectRowChanges
 *
 * @param {object} $row - jQuery table row element
 *
 * @returns {object}
 */
function detectRowChanges($row) {
  const original = JSON.parse($row.attr('data-original'));
  const changes = {};
  $row.find('.edit-cell').each(function () {
    const $input = $(this);
    const column = $input.data('column');
    let newValue = $input.val();
    const oldValue = original[column];
    if (String(newValue) !== String(oldValue)) {
      changes[column] = newValue;
    }
  });
  return changes;
}


/**
 * updates highlighting of table cells
 *
 * @function
 * @name updateRowHighlight
 *
 * @param {object} $row - jQuery table row element
 *
 * @returns {object}
 */
function updateRowHighlight($row) {
  const original = JSON.parse($row.attr('data-original'));
  $row.find('.edit-cell').each(function () {
    const $input = $(this);
    const column = $input.data('column');
    let newValue = $input.val();
    const oldValue = original[column];
    if (String(newValue) !== String(oldValue)) {
      $input.addClass('bg-warning');
    } else {
      $input.removeClass('bg-warning');
    }
  });
}


/**
 * updates state of row update button
 *
 * @function
 * @name updateRowButtonState
 *
 * @param {object} $row - jQuery table row element
 *
 * @returns {object}
 */
function updateRowButtonState($row) {
  const changes = detectRowChanges($row);
  const $updateRowButton = $row.find('.update-row');
  if (Object.keys(changes).length > 0) {
    enableFormElement($updateRowButton);
  } else {
    disableFormElement($updateRowButton);
  }
}


/**
 * renders passed update result
 *
 * @function
 * @name renderupdateResult
 *
 * @param {object} result - update result
 */
function renderupdateResult(result) {
  let title, body;
  if (result && result.success) {
    title = `<i class="fa-solid ${ICON_SUCCESS} text-success"></i> Aktualisierung erfolgreich`;
    body = `Es wurde(n) ${result.updated_rows} Zeile(n) erfolgreich aktualisiert.`;
  } else {
    title = `<i class="fa-solid ${ICON_ERROR} text-danger"></i> Aktualisierung fehlgeschlagen`;
    if (result.errors) {
      body = 'Beim Aktualisieren ist ein Datenbankfehler aufgetreten:';
      body += '<br><br>';
      body += `<p class="font-monospace">${result.errors[0].message}</p>`;
    } else {
      body = 'Beim Aktualisieren ist ein Fehler aufgetreten.';
    }
  }
  setModal($('#messages-modal'), title, body);
  $('#messages-modal').modal('show');
}
