/**
 * @file attributeFilter.js
 *
 * narrows the visible rows of a collection's attribute overview to those whose
 * attribute name contains the search term
 *
 * see docs/pygeoapi/rechtesystem.md for why this runs in the browser and why it
 * is a module of its own
 */

const HIDDEN_CLASS = 'attribute-filter-hidden';


/**
 * builds the status text of a filter pass
 *
 * @function
 * @name statusText
 *
 * @param {string} term - search term as typed
 * @param {number} matches - number of matching rows
 * @param {number} total - number of rows
 *
 * @returns {string}
 */
function statusText(term, matches, total) {
  if (!term) {
    return '';
  }
  if (!matches) {
    return `Kein Attribut enthält „${term}“. Zurücksetzen zeigt wieder alle ${total}.`;
  }
  return `${matches} von ${total} Attributen.`;
}


/**
 * indexes the rows of the overview once, so that a keystroke costs no DOM reads
 *
 * @function
 * @name indexRows
 *
 * @param {Element} group - inline group holding the overview
 *
 * @returns {Array<{row: Element, name: string}>}
 */
function indexRows(group) {
  const index = [];
  // the inline denies adding, so Django renders no empty form; excluded anyway
  for (const row of group.querySelectorAll('tr.form-row:not(.empty-form)')) {
    const cell = row.querySelector('td.field-name > p');
    if (cell) {
      index.push({row: row, name: cell.textContent.trim().toLowerCase()});
    }
  }
  return index;
}


/**
 * wires the search above a collection's attribute overview
 *
 * @function
 * @name initAttributeFilter
 *
 * @param {Document} doc - document to wire, the current one by default
 *
 * @returns {boolean} whether a search block was found and wired
 */
export function initAttributeFilter(doc = document) {
  const controls = doc.querySelector('.attribute-filter');
  if (!controls) {
    // no block on the add page and none for an empty inventory
    return false;
  }
  const input = controls.querySelector('.attribute-filter-input');
  const reset = controls.querySelector('.attribute-filter-reset');
  const status = controls.querySelector('.attribute-filter-status');
  const group = doc.getElementById(controls.dataset.group);
  if (!input || !reset || !status || !group) {
    return false;
  }
  const rows = indexRows(group);

  const apply = () => {
    const term = input.value.trim();
    const needle = term.toLowerCase();
    let matches = 0;
    for (const entry of rows) {
      const hidden = Boolean(needle) && !entry.name.includes(needle);
      // classList only: a row removed or disabled here would drop its role
      // assignment from the POST and the save would revoke it
      entry.row.classList.toggle(HIDDEN_CLASS, hidden);
      if (!hidden) {
        matches += 1;
      }
    }
    // textContent: the term must not reach the page as markup
    status.textContent = statusText(term, matches, rows.length);
  };

  input.addEventListener('input', apply);

  input.addEventListener('keydown', (event) => {
    // without this the implicit submission would save the collection
    if (event.key === 'Enter') {
      event.preventDefault();
    }
  });

  reset.addEventListener('click', () => {
    input.value = '';
    apply();
    input.focus();
  });

  // browsers restore field values on back and forward navigation
  apply();
  return true;
}
