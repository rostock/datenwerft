/**
 * @file asyncFunctions.js
 *
 * contains (helper) functions
 */

/**
 * clears dropdown
 *
 * @function
 * @name clearDropdown
 *
 * @param {object} $dropdown - dropdown object
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
 * disable form element
 *
 * @function
 * @name disableFormElement
 *
 * @param {object} $formElement - form element object
 */
function disableFormElement($formElement) {
  $formElement.prop('disabled', true);
}


/**
 * enable form element
 *
 * @function
 * @name enableFormElement
 *
 * @param {object} $formElement - form element object
 */
function enableFormElement($formElement) {
  $formElement.prop('disabled', false);
}


/**
 * populates dropdown
 *
 * @function
 * @name populateDropdown
 *
 * @param {object} $dropdown - dropdown object
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
 * populates table select dropdown
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
 * renders columns table
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
    <tbody>
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
 * normalizes strings for auto-matching
 *
 * @function
 * @name normalize
 *
 * @param {string} value
 *
 * @returns {string}
 */
function normalize(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}


/**
 * clears mapping UI
 *
 * @function
 * @name clearMappingTable
 */
function clearMappingTable() {
  $('#mapping-table').empty();
}


/**
 * renders mapping UI
 *
 * @function
 * @name renderMappingTable
 */
function renderMappingTable() {
  let tableStructure = `
    <thead>
      <tr>
        <th>Spaltenname in Zieltabelle</th>
        <th>Datentyp</th>
        <th>Pflicht?</th>
        <th>Spaltenname in Quelldatei</th>
        <th>Vorschau</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
    </tbody>
  `;
  $('#mapping-table').append(tableStructure);
  const $tbody = $('#mapping-table tbody');
  $.each(currentColumns, function (index, col) {
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
    const previewValue =
      currentPreviewRows.length
        ? Object.values(currentPreviewRows[0])[0]
        : '';
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
        <td>
          <select
            class="form-select mapping-select"
            data-db-column="${col.name}"
          >
            ${options}
          </select>
        </td>
        <td class="preview-cell">
          ${previewValue}
        </td>
      </tr>
    `;
    $tbody.append(row);
  });

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
 * populates year select dropdown
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
 * populates area select dropdown
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
 * populates election select dropdown
 *
 * @function
 * @name populateElectionSelect
 *
 * @param {Array<string>} elections - elections
 */
function populateElectionSelect(elections) {
  const $electionSelect = $('#election-select');
  $.each(elections, function (index, election) {
    let value = election.election + '___' + election.year;
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
 * builds data export URL
 *
 * @function
 * @name buildDataExportURL
 *
 * @param {string} baseURL
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
