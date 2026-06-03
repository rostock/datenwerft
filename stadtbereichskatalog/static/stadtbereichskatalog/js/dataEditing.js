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
    clearEditingTable();
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
    clearEditingTable();
    if (!schema || !table) {
      disableDataLoading();
      return;
    }
    enableDataLoading();
  });


  $('#load-data').on('click', async function() {
    const schema = $('#schema-select').val();
    const table = $('#table-select').val();
    if (!schema || !table) {
      return;
    }
    const columnsData = await fetchColumns(schema, table);
    if (!columnsData || !columnsData.columns) {
      return;
    }
    $.each(columnsData.columns, function(index, column) {
      if (column.primary_key) {
        primaryKeyColumns.push(column.name);
      }
    });
    const rowsData = await fetchData(schema, table, primaryKeyColumns);
    if (!rowsData || !rowsData.rows) {
      return;
    }
    renderEditingTable(columnsData.columns, rowsData.rows);
  });

});


$(document).on('input change', '.edit-cell', function() {
  const $row = $(this).closest('tr');
  updateRowHighlight($row);
  updateRowButtonState($row);
});


$(document).on('click', '.update-row', async function () {
  const schema = $('#schema-select').val();
  const table = $('#table-select').val();
  const $row = $(this).closest('tr');
  const pk = $row.data('pk');
  const changes = detectRowChanges($row);
  if (Object.keys(changes).length === 0) {
    return;
  }
  const result = await executeData(schema, table, pk, changes);
  if (result.success) {
    // update baseline
    const original = $row.data('original');
    Object.assign(original, changes);
    updateRowHighlight($row);
    updateRowButtonState($row);
  }
  renderupdateResult(result);
});
