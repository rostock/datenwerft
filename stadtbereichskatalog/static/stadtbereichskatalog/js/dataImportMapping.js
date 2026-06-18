/**
 * @file dataImportMapping.js
 *
 * handles data mapping and import
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    clearColumnsTable();
    clearMappingTable();
    disableUpload();
    disableImport();
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
    disableImport();
    if (!schema || !table) {
      disableUpload();
      return;
    }
    const data = await fetchColumns(schema, table);
    if (!data || !data.columns) {
      return;
    }
    currentColumns = data.columns;
    renderColumnsTable(currentColumns);
    enableUpload();
    if (currentCsvHeaders.length) {
      renderMappingTable();
      enableImport();
    }
  });


  $('#upload-file').on('click', async function() {
    const fileInput = $('#file-input')[0];
    if (!fileInput.files.length) {
      setModal(
        $('#messages-modal'),
        `<i class="fa-solid ${ICON_WARNING} text-warning"></i> Quelldatei fehlt`,
        'Bitte wählen Sie zunächst eine Quelldatei für den Upload aus.'
      );
      $('#messages-modal').modal('show');
      return;
    }
    const file = fileInput.files[0];
    const data = await fetchCsvPreview(file);
    if (!data) {
      return;
    }
    currentCsvHeaders = data.headers;
    currentPreviewRows = data.preview_rows;
    clearMappingTable();
    renderMappingTable();
    enableImport();
  });


  $('#import').on('click', async function() {
    const schema = $('#schema-select').val();
    const table = $('#table-select').val();
    const mappings = collectMappings();
    const fileInput = $('#file-input')[0];
    const file = fileInput.files[0];
    const result = await executeImport(schema, table, mappings, file);
    renderImportResult(result);
  });

});


$(document).on('change', '.mapping-select', function() {
  updatePreview($(this));
  validateMappings();
});
