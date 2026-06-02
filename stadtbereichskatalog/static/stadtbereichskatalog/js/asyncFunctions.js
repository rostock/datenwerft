/**
 * @file asyncFunctions.js
 *
 * contains asynchronous (helper) functions
 */

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
 * uploads passed CSV file and fetches preview
 *
 * @async
 * @function
 * @name fetchCsvPreview
 *
 * @param {File} file - CSV file
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
 * executes import of passed file into passed table within passed database schema accoring to passed mapping
 *
 * @async
 * @function
 * @name executeImport
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 * @param {object} mappings - mapping configuration
 * @param {File} file - file
 *
 * @returns {Promise<object|null>}
 */
async function executeImport(schema, table, mappings, file) {
  try {
    const formData = new FormData();
    formData.append('schema', schema);
    formData.append('table', table);
    formData.append('mappings', JSON.stringify(mappings));
    formData.append('file', file);
    const response = await fetch(
      IMPORT_URL,
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
 * fetches all distinct years of passed table within passed database schema
 *
 * @async
 * @function
 * @name fetchYears
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 *
 * @returns {Promise<object|null>}
 */
async function fetchYears(schema, table) {
  try {
    const response = await fetch(
      `${GET_DISTINCT_YEARS_URL}?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
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
 * fetches all distinct areas of passed table within passed database schema
 *
 * @async
 * @function
 * @name fetchAreas
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 *
 * @returns {Promise<object|null>}
 */
async function fetchAreas(schema, table) {
  try {
    const response = await fetch(
      `${GET_DISTINCT_AREAS_URL}?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
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
 * fetches all distinct elections of passed table within passed database schema
 *
 * @async
 * @function
 * @name fetchElections
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 *
 * @returns {Promise<object|null>}
 */
async function fetchElections(schema, table) {
  try {
    const response = await fetch(
      `${GET_DISTINCT_ELECTIONS_URL}?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
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
 * executes deletion of data from passed table within passed database schema accoring to passed filters
 *
 * @async
 * @function
 * @name executeDeletion
 *
 * @param {string} schema - name of database schema
 * @param {string} table - name of database table
 * @param {string} year - year filter
 * @param {string} election - election filter
 *
 * @returns {Promise<object|null>}
 */
async function executeDeletion(schema, table, year, election) {
  try {
    const formData = new FormData();
    formData.append('schema', schema);
    formData.append('table', table);
    formData.append('year', year);
    formData.append('election', election);
    const response = await fetch(
      DELETION_URL,
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
