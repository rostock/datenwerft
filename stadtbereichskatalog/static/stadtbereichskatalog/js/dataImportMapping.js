/**
 * @file dataImportMapping.js
 *
 * handles database schema and table selection as well as table structure inspection
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    clearColumnsTable();
    clearMappingTable();
    disableUpload();
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
    enableUpload();
  });


  $('#upload-file').on('click', async function() {
    const fileInput = $('#file-input')[0];
    if (!fileInput.files.length) {
      toggleModal(
        $('#messages-modal'),
        'Keine Quelldatei ausgewählt!',
        'Bitte wählen Sie zunächst eine Quelldatei aus.'
      );
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
