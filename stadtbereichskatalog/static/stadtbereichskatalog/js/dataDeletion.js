/**
 * @file dataDeletion.js
 *
 * handles database schema and table selection as well as data deletion
 */

$(document).ready(function() {

  $('#schema-select').on('change', async function() {
    const schema = $(this).val();
    resetTableSelect();
    resetYearSelect();
    disableDeletion();
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
    disableDeletion();
    if (!schema || !table) {
      return;
    }

    // selections generally only if table other than 'kandidaten' selected
    if (table !== 'kandidaten') {

      // election generally only if table other than 'kandidaten' selected
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

      }

    }
  });


  $('#year-select').on('change', async function() {
    const schema = $('#schema-select').val();
    const table = $('#table-select').val();
    const year = $(this).val();
    if (!schema || !table || !year) {
      disableDeletion();
      return;
    }
    enableDeletion();
  });


  $('#election-select').on('change', async function() {
    const schema = $('#schema-select').val();
    const table = $('#table-select').val();
    const election = $(this).val();
    if (!schema || !table || !election) {
      disableDeletion();
      return;
    }
    enableDeletion();
  });


  $('#deletion').on('click', async function() {
    const schema = $('#schema-select').val();
    const table = $('#table-select').val();
    const year = $('#year-select').val();
    const election = $('#election-select').val();
    const result = await executeDeletion(schema, table, year, election);
    renderDeletionResult(result);
  });

});
