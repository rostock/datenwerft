/* global $, toggleModal */
/* eslint no-undef: "error" */

/**
 * @function
 * @name subsetting
 *
 * behandelt und übergibt eine Filtermenge
 *
 * @param {string[]} keys - Liste mit Primärschlüsseln von Objekten einer Filtermenge
 * @param {string} subsetURL - URL des Toolbox-Views zum Erstellen eines neuen Subsets
 * @param {string} modelName - Name des Datenmodells mit den Objekten
 * @param {string} modelPrimaryKeyField - Feld mit Primärschlüsseln im Datenmodell mit den Objekten
 * @param {string} successURL - URL zum Öffnen im Erfolgsfall
 * @param {string} errorText - Text für Fehlermeldung
 */
function subsetting(keys, subsetURL, modelName, modelPrimaryKeyField, successURL, errorText) {
  let errorModalTitle = 'Keine Übernahme der aktuellen Filtermenge möglich!';
  if (keys.length > 0) {
    // Liste mit Primärschlüsseln von Objekten einer Filtermenge in JSON umwandeln
    let pk_values = JSON.stringify(keys);
    // POST-Request an Toolbox-View zum Erstellen eines neuen Subsets senden
    fetch(subsetURL, {
      method: 'POST',
      body: new URLSearchParams({
        app_label: 'datenmanagement',
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
          'Bei der Übernahme der aktuellen Filtermenge ist ein Serverfehler aufgetreten.'
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
