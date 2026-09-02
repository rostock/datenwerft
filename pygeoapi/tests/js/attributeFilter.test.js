/**
 * @file attributeFilter.test.js
 * @vitest-environment jsdom
 *
 * unit tests of the search above a collection's attribute overview
 *
 * the fixture mirrors the markup Django's tabular inline renders; that it really
 * does is asserted in pygeoapi/tests/test_collection_admin.py
 */

import {beforeEach, describe, expect, it} from 'vitest';

import {initAttributeFilter} from '../../static/pygeoapi/js/attributeFilter.js';

const HIDDEN_CLASS = 'attribute-filter-hidden';


/**
 * one row of the overview, with the fields that must survive every filter pass
 *
 * @param {number} index - index of the row within the formset
 * @param {string} name - name of the attribute
 *
 * @returns {string}
 */
function rowMarkup(index, name) {
  return `
    <tr class="form-row has_original" id="attributes-${index}">
      <td class="original">
        <p>Kollektion 7 → ${name}</p>
        <input type="hidden" name="attributes-${index}-id" value="${index + 1}">
        <input type="hidden" name="attributes-${index}-collection" value="7">
      </td>
      <td class="field-name"><p>${name}</p></td>
      <td class="field-data_type"><p>text</p></td>
      <td class="field-hint"><p></p></td>
      <td class="field-roles">
        <select name="attributes-${index}-roles" class="select2" data-attribute="${name}" multiple>
          <option value="1"${index % 2 ? ' selected' : ''}>Grünamt (gruen)</option>
          <option value="2">Tiefbauamt (tief)</option>
        </select>
      </td>
    </tr>`;
}


/**
 * builds the attribute overview of a collection and wires the filter
 *
 * @param {Array<string>} names - attribute names, in the order of the overview
 */
function fixture(names) {
  document.body.innerHTML = `
    <form id="collection_form" method="post">
      <div class="attribute-filter" data-group="attributes-group">
        <label for="attribute-filter-input">Attribut suchen:</label>
        <input type="search" id="attribute-filter-input" class="attribute-filter-input">
        <button type="button" class="attribute-filter-reset">Zurücksetzen</button>
        <p class="attribute-filter-status" role="status"></p>
      </div>
      <div class="js-inline-admin-formset inline-group" id="attributes-group">
        <input type="hidden" name="attributes-TOTAL_FORMS" value="${names.length}">
        <input type="hidden" name="attributes-INITIAL_FORMS" value="${names.length}">
        <input type="hidden" name="attributes-MIN_NUM_FORMS" value="0">
        <input type="hidden" name="attributes-MAX_NUM_FORMS" value="1000">
        <table>
          <tbody>${names.map((name, index) => rowMarkup(index, name)).join('')}</tbody>
        </table>
      </div>
    </form>`;
  expect(initAttributeFilter(document)).toBe(true);
}


/**
 * types into the search field
 *
 * @param {string} value - search term
 */
function search(value) {
  const input = document.querySelector('.attribute-filter-input');
  input.value = value;
  input.dispatchEvent(new Event('input', {bubbles: true}));
}


/**
 * the names of the rows that are visible right now
 *
 * @returns {Array<string>}
 */
function visibleNames() {
  return [...document.querySelectorAll('#attributes-group tr.form-row')]
    .filter((row) => !row.classList.contains(HIDDEN_CLASS))
    .map((row) => row.querySelector('td.field-name > p').textContent);
}


/**
 * the status text below the search field
 *
 * @returns {string}
 */
function statusText() {
  return document.querySelector('.attribute-filter-status').textContent;
}


/**
 * every name/value pair the inline would post, plus whether the field is
 * disabled – a disabled field is not submitted at all
 *
 * @returns {Array<Array>}
 */
function postedState() {
  return [...document.querySelectorAll('#attributes-group [name]')].map((element) => [
    element.name,
    element.multiple
      ? [...element.selectedOptions].map((option) => option.value)
      : element.value,
    element.disabled,
  ]);
}


describe('initAttributeFilter', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it('does nothing without a search block', () => {
    document.body.innerHTML = '<form></form>';
    expect(initAttributeFilter(document)).toBe(false);
  });

  it('narrows the rows to the attributes containing the term', () => {
    fixture(['baumart', 'strasse', 'strassenname', 'hoehe']);
    search('strasse');
    expect(visibleNames()).toEqual(['strasse', 'strassenname']);
  });

  it('ignores upper and lower case on both sides', () => {
    fixture(['Baumart', 'STRASSE', 'hoehe']);
    search('sTrAsSe');
    expect(visibleNames()).toEqual(['STRASSE']);
    search('baum');
    expect(visibleNames()).toEqual(['Baumart']);
  });

  it('shows every row again for an empty term', () => {
    fixture(['baumart', 'strasse']);
    search('baum');
    expect(visibleNames()).toEqual(['baumart']);
    search('');
    expect(visibleNames()).toEqual(['baumart', 'strasse']);
    expect(statusText()).toBe('');
  });

  it('names the number of matches while filtering', () => {
    fixture(['baumart', 'strasse', 'strassenname']);
    search('strasse');
    expect(statusText()).toBe('2 von 3 Attributen.');
  });

  it('explains an empty result instead of showing an empty table', () => {
    fixture(['baumart', 'strasse']);
    search('gibtesnicht');
    expect(visibleNames()).toEqual([]);
    expect(statusText()).toContain('Kein Attribut enthält „gibtesnicht“');
    expect(statusText()).toContain('Zurücksetzen');
  });

  it('puts the term into the status as text and not as markup', () => {
    fixture(['baumart']);
    search('<img src=x onerror=alert(1)>');
    const status = document.querySelector('.attribute-filter-status');
    expect(status.querySelector('img')).toBeNull();
    expect(status.textContent).toContain('<img src=x onerror=alert(1)>');
  });

  it('restores the full list on reset and returns the focus', () => {
    fixture(['baumart', 'strasse', 'hoehe']);
    search('baum');
    expect(visibleNames()).toEqual(['baumart']);
    document.querySelector('.attribute-filter-reset').click();
    expect(visibleNames()).toEqual(['baumart', 'strasse', 'hoehe']);
    expect(document.querySelector('.attribute-filter-input').value).toBe('');
    expect(statusText()).toBe('');
    expect(document.activeElement).toBe(document.querySelector('.attribute-filter-input'));
  });

  it('suppresses the implicit submission on Enter', () => {
    fixture(['baumart']);
    let submitted = false;
    document.querySelector('#collection_form').addEventListener('submit', () => {
      submitted = true;
    });
    const event = new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true});
    document.querySelector('.attribute-filter-input').dispatchEvent(event);
    // defaultPrevented carries the test: jsdom implements no implicit submission,
    // so `submitted` would stay false even without the handler under test
    expect(event.defaultPrevented).toBe(true);
    expect(submitted).toBe(false);
  });

  it('leaves other keys alone', () => {
    fixture(['baumart']);
    const event = new KeyboardEvent('keydown', {key: 'a', bubbles: true, cancelable: true});
    document.querySelector('.attribute-filter-input').dispatchEvent(event);
    expect(event.defaultPrevented).toBe(false);
  });

  it('keeps the posted state identical through filtering and resetting', () => {
    fixture(['baumart', 'strasse', 'strassenname', 'hoehe', 'id']);
    const before = postedState();
    search('strasse');
    expect(visibleNames()).toEqual(['strasse', 'strassenname']);
    expect(postedState()).toEqual(before);
    // and again with every row hidden
    search('gibtesnicht');
    expect(visibleNames()).toEqual([]);
    expect(postedState()).toEqual(before);
    document.querySelector('.attribute-filter-reset').click();
    expect(postedState()).toEqual(before);
  });

  it('keeps the management fields of the formset untouched', () => {
    fixture(['baumart', 'strasse', 'hoehe']);
    search('baum');
    // changed counts here would make the save drop rows
    expect(document.querySelector('[name="attributes-TOTAL_FORMS"]').value).toBe('3');
    expect(document.querySelector('[name="attributes-INITIAL_FORMS"]').value).toBe('3');
    expect(document.querySelectorAll('#attributes-group tr.form-row')).toHaveLength(3);
  });

  it('hides by class only and never removes a row', () => {
    fixture(['baumart', 'strasse']);
    search('baum');
    const hidden = document.querySelector('#attributes-1');
    expect(hidden).not.toBeNull();
    expect(hidden.classList.contains(HIDDEN_CLASS)).toBe(true);
    expect(hidden.querySelector('select[name="attributes-1-roles"]')).not.toBeNull();
    expect(hidden.querySelector('select[name="attributes-1-roles"]').disabled).toBe(false);
  });

  it('stays responsive with 500 rows', () => {
    const names = Array.from({length: 500}, (unused, index) => `attribut_${index}`);
    fixture(names);
    const before = postedState();
    const started = performance.now();
    search('attribut_1');
    const elapsed = performance.now() - started;
    // attribut_1, attribut_1x and attribut_1xx
    expect(visibleNames()).toHaveLength(111);
    expect(postedState()).toEqual(before);
    // guards against an accidentally quadratic pass, no performance promise
    expect(elapsed).toBeLessThan(1000);
  });
});
