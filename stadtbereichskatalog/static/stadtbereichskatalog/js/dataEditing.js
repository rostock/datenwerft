/**
 * @file dataEditing.js
 *
 * handles data editing
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    disableDataLoading();
    clearColumnsTable();
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
    if (!schema || !table) {
      disableDataLoading();
      return;
    }
    const data = await fetchColumns(schema, table);
    if (!data || !data.columns) {
      return;
    }
    currentColumns = data.columns;
    renderColumnsTable(currentColumns);
    enableDataLoading();
  });

});
