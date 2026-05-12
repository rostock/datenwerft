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
    if (!schema || !table) {
      return;
    }
    const yearsData = await fetchYears(schema, table);
    if (!yearsData || !yearsData.years) {
      return;
    }
    populateYearSelect(yearsData.years);
    const areasData = await fetchAreas(schema, table);
    if (!areasData || !areasData.areas) {
      return;
    }
    populateAreaSelect(areasData.areas);
  });

});
