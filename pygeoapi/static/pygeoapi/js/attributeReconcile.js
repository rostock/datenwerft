/**
 * @file attributeReconcile.js
 *
 * triggers the reconciliation of a collection's attribute inventory: fetches the
 * column list of the source table and hands it to the regular save of the change
 * page
 *
 * see docs/pygeoapi/rechtesystem.md for the data path through the browser
 */

const FETCHING = 'Spaltenliste wird geholt …';
const NO_SOURCE = 'Bitte zuerst Datenbankverbindung, Schema und Tabelle/View angeben.';
const UNCHANGED = 'Das Attributinventar bleibt unverändert.';
// the cause is named as far as it can be told apart, but never with host, user
// or password of the database connection
const UNREACHABLE = 'Die Quelle antwortet nicht.';
const FAULTY_ANSWER = 'Die Spaltenauskunft meldet einen Fehler.';
const NO_COLUMNS = 'Die Quelle liefert keine Spalten – bitte Schema und Tabelle/View prüfen.';


/**
 * fetches name and data type of every column of the collection's source table
 *
 * @async
 * @function
 * @name fetchColumns
 *
 * @param {string} url - url of the column information
 * @param {string} db - database connection
 * @param {string} schema - name of the schema
 * @param {string} table - name of the table/view
 *
 * @returns {Promise<object>} the columns, or the cause why there are none
 */
async function fetchColumns(url, db, schema, table) {
  const query = [
    `db=${encodeURIComponent(db)}`,
    `schema=${encodeURIComponent(schema)}`,
    `table=${encodeURIComponent(table)}`
  ].join('&');
  let response;
  try {
    response = await fetch(`${url}?${query}`, {method: 'GET'});
  } catch (error) {
    console.error(error);
    return {cause: UNREACHABLE};
  }
  if (!response.ok) {
    return {cause: FAULTY_ANSWER};
  }
  let data;
  try {
    data = await response.json();
  } catch (error) {
    console.error(error);
    return {cause: FAULTY_ANSWER};
  }
  if (!Array.isArray(data.columns)) {
    return {cause: FAULTY_ANSWER};
  }
  if (!data.columns.length) {
    return {cause: NO_COLUMNS};
  }
  return {columns: data.columns};
}


/**
 * wires the button that triggers the reconciliation
 *
 * @function
 * @name initAttributeReconcile
 *
 * @param {Document} doc - document to wire, the current one by default
 *
 * @returns {boolean} whether a reconcile block was found and wired
 */
export function initAttributeReconcile(doc = document) {
  const button = doc.querySelector('.attribute-reconcile-button');
  if (!button) {
    // no block on the add page, where the source is not saved yet
    return false;
  }
  const status = doc.querySelector('.attribute-reconcile-status');
  const marker = doc.querySelector('#id_reconcile');
  const columnsField = doc.querySelector('#id_reconcile_columns');
  const form = button.closest('form');
  if (!status || !marker || !columnsField || !form) {
    return false;
  }
  // browsers restore field values on back navigation; a restored marker would
  // turn the next ordinary save into a reconcile nobody asked for
  marker.value = '';
  columnsField.value = '';

  button.addEventListener('click', async () => {
    // the model fields, not the *_select helper lists, which stay empty until
    // someone picks a schema and a table by hand
    const db = doc.querySelector('#id_database_connection');
    const schema = doc.querySelector('#id_schema');
    const table = doc.querySelector('#id_table');
    if (!db || !schema || !table) {
      return;
    }
    const source = [db.value, schema.value.trim(), table.value.trim()];
    if (!source.every(Boolean)) {
      status.textContent = NO_SOURCE;
      return;
    }
    button.disabled = true;
    status.textContent = FETCHING;
    const {columns, cause} = await fetchColumns(button.dataset.columnsUrl, ...source);
    if (cause) {
      // no submit: saving and reloading the configuration for nothing would be
      // the wrong answer to an unreachable source
      status.textContent = `${cause} ${UNCHANGED}`;
      button.disabled = false;
      return;
    }
    marker.value = '1';
    columnsField.value = JSON.stringify(columns);
    // stays on the change page, so that the overview shows the new state; added
    // here because a rendered field would do this on every ordinary save
    const stay = doc.createElement('input');
    stay.type = 'hidden';
    stay.name = '_continue';
    stay.value = '1';
    form.appendChild(stay);
    form.submit();
  });

  return true;
}
