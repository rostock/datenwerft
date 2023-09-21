/**
 * @function
 * @name subsetting
 *
 * handles and passes a filter set
 *
 * @param {string[]} keys - list of primary keys of objects of a filter set
 * @param {string} subsetURL - URL of Toolbox app view for creating a subset
 * @param {string} modelName - name of the model with the objects
 * @param {string} modelPrimaryKeyField - name of the primary key field of the model with the objects
 * @param {string} successURL - URL to open if successful
 * @param {string} errorText - text for error message
 * @param {string} [appLabel='datenmanagement'] - app label
 */
function subsetting(keys, subsetURL, modelName, modelPrimaryKeyField, successURL, errorText, appLabel='datenmanagement') {
  let errorModalTitle = 'Keine Übernahme der aktuellen Filtermenge möglich!';
  if (keys.length > 0) {
    // convert list of primary keys of objects of a filter set to JSON
    let pk_values = JSON.stringify(keys);
    // send POST request to appropriate Toolbox app view for creating a subset
    fetch(subsetURL, {
      method: 'POST',
      body: new URLSearchParams({
        app_label: appLabel,
        model_name: modelName.toLowerCase(),
        pk_field: modelPrimaryKeyField,
        pk_values: pk_values
      })
    })
    .then(response => response.json())
    .then(data => {
      let subset_id = JSON.parse(data).id;
      window.open(successURL.replace(/worschdsupp/, subset_id.toString()), '_blank', 'noopener,noreferrer');
    })
    .catch(
      (error) => {
        console.error(error);
        toggleModal(
          $('#error-modal'),
          errorModalTitle,
          errorText ? errorText : 'Bei der Übernahme der aktuellen Filtermenge ist ein Serverfehler aufgetreten.'
        );
      }
    );
  } else
    toggleModal(
      $('#error-modal'),
      errorModalTitle,
      'Die aktuelle Filtermenge ist leer.'
    );
}
