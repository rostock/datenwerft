/**
 * @file data_import_mapping.js
 *
 * handles database schema and table selection as well as table structure inspection
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    clearColumnsTable();
    clearMappingTable();
    if (!schema) {
      return;
    }
    const data = await fetchTables(schema);
    if (!data || !data.tables) {
      return;
    }
    populateTableSelect(data.tables);
  });


  $('#table-select').on('change', async function() {
    const schema = $('#schema-select').val();
    const table = $(this).val();
    clearColumnsTable();
    clearMappingTable();
    if (!schema || !table) {
      return;
    }
    const data = await fetchColumns(schema, table);
    if (!data || !data.columns) {
      return;
    }
    currentColumns = data.columns;
    renderColumnsTable(currentColumns);
    if (currentCsvHeaders.length) {
      renderMappingTable();
    }
  });


  $('#upload-file').on('click', async function() {
    const fileInput = $('#file-input')[0];
    if (!fileInput.files.length) {
      alert('Bitte wählen Sie eine Quelldatei aus.');
      return;
    }
    const file = fileInput.files[0];
    const data = await fetchCsvPreview(file);
    if (!data) {
      return;
    }
    currentCsvHeaders = data.headers;
    currentPreviewRows = data.preview_rows;
    renderMappingTable();
  });

});


/**
 * fetches all tables of passed database schema
 *
 * @async
 * @function
 * @name fetchTables
 *
 * @param {string} schema - name of database schema
 *
 * @returns {Promise<object|null>}
 */
async function fetchTables(schema) {
  try {
    const response = await fetch(
      `${GET_DATABASE_TABLES_URL}?schema=${encodeURIComponent(schema)}`,
      {
        method: 'GET'
      }
    );
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}


/**
 * fetches all columns of passed table within passed database schema
 *
 * @async
 * @function
 * @name fetchColumns
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 *
 * @returns {Promise<object|null>}
 */
async function fetchColumns(schema, table) {
  try {
    const response = await fetch(
      `${GET_DATABASE_COLUMNS_URL}?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
      {
        method: 'GET'
      }
    );
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}


/**
 * resets table select dropdown
 *
 * @function
 * @name resetTableSelect
 */
function resetTableSelect() {
  const $tableSelect = $('#table-select');
  $tableSelect.empty();
  $tableSelect.append(
    $('<option>', {
      value: '',
      text: '---------'
    })
  );
  $tableSelect.prop('disabled', true);
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
  const $tableSelect = $('#table-select');
  $.each(tables, function (index, table) {
    $tableSelect.append(
      $('<option>', {
        value: table,
        text: table
      })
    );
  });
  $tableSelect.prop('disabled', false);
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
 * uploads CSV and fetches preview
 *
 * @async
 * @function
 * @name fetchCsvPreview
 *
 * @param {File} file
 *
 * @returns {Promise<object|null>}
 */
async function fetchCsvPreview(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(
      PREVIEW_CSV_URL,
      {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': CSRF_TOKEN
        }
      }
    );
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
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
