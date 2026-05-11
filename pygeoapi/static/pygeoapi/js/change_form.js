/**
 * @file change_form.js
 *
 * handles database schema, table, and multiple columns selections
 */

$(document).ready(function() {

  $('.select2').select2({});

  $('#id_database_connection').on('change', async function() {
    const db = $(this).val();
    resetSchemaSelect();
    resetTableSelect();
    resetFieldSelects();
    if (!db) {
      return;
    }
    const data = await fetchSchemas(db);
    if (!data || !data.schemas) {
      return;
    }
    populateSchemaSelect(data.schemas);
  });

  $('#id_schema_select').on('change', async function() {
    const db = $('#id_database_connection').val();
    const schema = $(this).val();
    resetTableSelect();
    resetFieldSelects();
    if (!db || !schema) {
      return;
    }
    $('#id_schema').val(schema);
    const data = await fetchTables(db, schema);
    if (!data || !data.tables) {
      return;
    }
    populateTableSelect(data.tables);
  });

  $('#id_table_select').on('change', async function() {
    const db = $('#id_database_connection').val();
    const schema = $('#id_schema_select').val();
    const table = $(this).val();
    resetFieldSelects();
    if (!db || !schema || !table) {
      return;
    }
    $('#id_table').val(table);
    const data = await fetchColumns(db, schema, table);
    if (!data || !data.columns) {
      return;
    }
    populateFieldSelects(data.columns);
  });

  $('#id_id_field_select').on('change', function() {
    const idField = $(this).val();
    if (!idField) {
      return;
    }
    $('#id_id_field').val(idField);
  });

  $('#id_title_field_select').on('change', function() {
    const titleField = $(this).val();
    if (!titleField) {
      return;
    }
    $('#id_title_field').val(titleField);
  });

  $('#id_geom_field_select').on('change', function() {
    const geomField = $(this).val();
    if (!geomField) {
      return;
    }
    $('#id_geom_field').val(geomField);
  });

  if ($('#id_database_connection').val()) {
    $('#id_database_connection').trigger('change');
  } else {
    resetSchemaSelect();
    resetTableSelect();
    resetFieldSelects();
  }

});


/**
 * fetches all schemas of passed database
 *
 * @async
 * @function
 * @name fetchSchemas
 *
 * @param {string} db - database connection
 *
 * @returns {Promise<object|null>}
 */
async function fetchSchemas(db) {
  try {
    const response = await fetch(
      `/pygeoapi/get-database-schemas?db=${encodeURIComponent(db)}`,
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
 * fetches all tables of passed schema of passed database
 *
 * @async
 * @function
 * @name fetchTables
 *
 * @param {string} db - database connection
 * @param {string} schema - name of schema
 *
 * @returns {Promise<object|null>}
 */
async function fetchTables(db, schema) {
  try {
    const response = await fetch(
      `/pygeoapi/get-database-tables?db=${encodeURIComponent(db)}&schema=${encodeURIComponent(schema)}`,
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
 * fetches all columns of passed table within passed schema of passed database
 *
 * @async
 * @function
 * @name fetchColumns
 *
 * @param {string} db - database connection
 * @param {string} schema - name of schema
 * @param {string} table - name of table
 *
 * @returns {Promise<object|null>}
 */
async function fetchColumns(db, schema, table) {
  try {
    const response = await fetch(
      `/pygeoapi/get-database-columns?db=${encodeURIComponent(db)}&schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
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
 * clears dropdown
 *
 * @function
 * @name clearDropdown
 *
 * @param {object} dropdown - dropdown object
 */
function clearDropdown(dropdown) {
  dropdown.empty();
  dropdown.append(
    $('<option>', {
      value: '',
      text: '---------'
    })
  );
  dropdown.prop('disabled', true);
}


/**
 * resets schema select dropdown
 *
 * @function
 * @name resetSchemaSelect
 */
function resetSchemaSelect() {
  clearDropdown($('#id_schema_select'));
}


/**
 * resets table select dropdown
 *
 * @function
 * @name resetTableSelect
 */
function resetTableSelect() {
  clearDropdown($('#id_table_select'));
}


/**
 * resets field select dropdowns
 *
 * @function
 * @name resetFieldSelects
 */
function resetFieldSelects() {
  clearDropdown($('#id_id_field_select'));
  clearDropdown($('#id_title_field_select'));
  clearDropdown($('#id_geom_field_select'));
}


/**
 * populates dropdown
 *
 * @function
 * @name populateDropdown
 *
 * @param {object} dropdown - dropdown object
 * @param {Array<string>} values - values
 */
function populateDropdown(dropdown, values) {
  $.each(values, function (index, value) {
    dropdown.append(
      $('<option>', {
        value: value,
        text: value
      })
    );
  });
  dropdown.prop('disabled', false);
}


/**
 * populates schema select dropdown
 *
 * @function
 * @name populateSchemaSelect
 *
 * @param {Array<string>} schemas - schema names
 */
function populateSchemaSelect(schemas) {
  populateDropdown($('#id_schema_select'), schemas);
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
  populateDropdown($('#id_table_select'), tables);
}


/**
 * populates field select dropdowns
 *
 * @function
 * @name populateFieldSelects
 *
 * @param {Array<string>} columns - column names
 */
function populateFieldSelects(columns) {
  populateDropdown($('#id_id_field_select'), columns);
  populateDropdown($('#id_title_field_select'), columns);
  populateDropdown($('#id_geom_field_select'), columns);
}
