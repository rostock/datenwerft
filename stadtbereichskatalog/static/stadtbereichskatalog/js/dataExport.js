/**
 * @file dataExport.js
 *
 * handles database schema and table selection as well as export data filtering
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    resetYearSelect();
    resetAreaSelect();
    resetElectionSelect();
    disableExport();
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
    resetYearSelect();
    resetAreaSelect();
    resetElectionSelect();
    if (!schema || !table) {
      disableExport();
      return;
    }

    // selections generally only if table other than 'kandidaten' selected
    if (table !== 'kandidaten') {

      // election selection if schema 'wahlen' selected
      if (schema === 'wahlen') {
        const electionsData = await fetchElections(schema, table);
        if (!electionsData || !electionsData.elections) {
          return;
        }
        populateElectionSelect(electionsData.elections);
      // year selection if schema other than 'wahlen' selected
      } else {
        const yearsData = await fetchYears(schema, table);
        if (!yearsData || !yearsData.years) {
          return;
        }
        populateYearSelect(yearsData.years);
      }

      // area selection only if table other than '_hro*' selected
      if (!table.startsWith('_hro')) {
        const areasData = await fetchAreas(schema, table);
        if (!areasData || !areasData.areas) {
          return;
        }
        populateAreaSelect(areasData.areas);
      }

    }

    enableExport();
  });


  $('#export-csv-standard').on('click', function() {
    window.location.href = buildDataExportURL(EXPORT_CSV_STANDARD_URL);
  });


  $('#export-csv-excel').on('click', function() {
    window.location.href = buildDataExportURL(EXPORT_CSV_EXCEL_URL);
  });


  $('#export-excel').on('click', function() {
    window.location.href = buildDataExportURL(EXPORT_EXCEL_URL);
  });

});
