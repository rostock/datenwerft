/**
 * @file attributeReconcile.test.js
 * @vitest-environment jsdom
 *
 * unit tests of the button that triggers the reconciliation of a collection's
 * attribute inventory
 *
 * the fixture mirrors the markup the change page renders; that it really does is
 * asserted in pygeoapi/tests/test_collection_admin.py
 */

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import {initAttributeReconcile} from '../../static/pygeoapi/js/attributeReconcile.js';

const COLUMNS_URL = '/pygeoapi/get-database-columns/';


/**
 * builds the change page of a collection and wires the button
 *
 * jsdom implements no form submission, so submit() is replaced by a spy
 *
 * @param {object} source - values of the model fields of the database source
 *
 * @returns {object} the submit spy of the form
 */
function fixture({db = '7', schema = 'public', table = 'baeume'} = {}) {
  document.body.innerHTML = `
    <form id="collection_form" method="post">
      <select id="id_database_connection" name="database_connection">
        <option value="">---------</option>
        <option value="${db}" selected>localhost</option>
      </select>
      <input type="text" id="id_schema" name="schema" value="${schema}">
      <input type="text" id="id_table" name="table" value="${table}">
      <div class="attribute-reconcile">
        <button type="button"
                class="attribute-reconcile-button"
                data-columns-url="${COLUMNS_URL}">Attribute abgleichen</button>
        <p class="attribute-reconcile-status" role="status"></p>
      </div>
      <input type="hidden" name="reconcile" id="id_reconcile">
      <input type="hidden" name="reconcile_columns" id="id_reconcile_columns">
    </form>`;
  const submit = vi.fn();
  document.querySelector('#collection_form').submit = submit;
  expect(initAttributeReconcile(document)).toBe(true);
  return submit;
}


/**
 * answers the next fetch with the given columns
 *
 * @param {Array<object>} columns - columns of the source table
 */
function answerWith(columns) {
  global.fetch = vi.fn(() =>
    Promise.resolve({ok: true, json: () => Promise.resolve({columns: columns})})
  );
}


/**
 * clicks the button and waits for its handler to run through
 */
async function click() {
  document.querySelector('.attribute-reconcile-button').click();
  await new Promise((resolve) => {
    setTimeout(resolve, 0);
  });
}


/**
 * the value of a hidden field of the reconcile
 *
 * @param {string} id - id of the field
 *
 * @returns {string}
 */
function fieldValue(id) {
  return document.querySelector(`#${id}`).value;
}


/**
 * the status text below the button
 *
 * @returns {string}
 */
function statusText() {
  return document.querySelector('.attribute-reconcile-status').textContent;
}


describe('initAttributeReconcile', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.restoreAllMocks();
    delete global.fetch;
  });

  it('does nothing without a reconcile block', () => {
    document.body.innerHTML = '<form></form>';
    expect(initAttributeReconcile(document)).toBe(false);
  });

  it('does nothing without the hidden fields', () => {
    document.body.innerHTML = `
      <form>
        <button type="button" class="attribute-reconcile-button" data-columns-url="/x/"></button>
        <p class="attribute-reconcile-status"></p>
      </form>`;
    expect(initAttributeReconcile(document)).toBe(false);
  });

  it('hands the fetched columns to the form and submits', async () => {
    const submit = fixture();
    answerWith([
      {name: 'id', type: 'integer'},
      {name: 'baumart', type: 'text'}
    ]);
    await click();
    expect(fieldValue('id_reconcile')).toBe('1');
    expect(JSON.parse(fieldValue('id_reconcile_columns'))).toEqual([
      {name: 'id', type: 'integer'},
      {name: 'baumart', type: 'text'}
    ]);
    expect(submit).toHaveBeenCalledOnce();
  });

  it('asks the endpoint for the saved source of the collection', async () => {
    fixture({db: '7', schema: 'grün amt', table: 'bäume'});
    answerWith([{name: 'id', type: 'integer'}]);
    await click();
    const [url] = global.fetch.mock.calls[0];
    expect(url.startsWith(`${COLUMNS_URL}?`)).toBe(true);
    const query = new URLSearchParams(url.split('?')[1]);
    // the model fields and not the *_select helper lists, which are empty on load
    expect(query.get('db')).toBe('7');
    expect(query.get('schema')).toBe('grün amt');
    expect(query.get('table')).toBe('bäume');
  });

  it('returns to the change page instead of the changelist', async () => {
    fixture();
    answerWith([{name: 'id', type: 'integer'}]);
    await click();
    const stay = document.querySelector('#collection_form [name="_continue"]');
    expect(stay).not.toBeNull();
    expect(stay.type).toBe('hidden');
  });

  it('names an empty result and submits nothing', async () => {
    const submit = fixture();
    answerWith([]);
    await click();
    expect(statusText()).toContain('liefert keine Spalten');
    expect(statusText()).toContain('bleibt unverändert');
    // no save and thus no configuration reload for nothing
    expect(submit).not.toHaveBeenCalled();
    expect(fieldValue('id_reconcile')).toBe('');
    expect(fieldValue('id_reconcile_columns')).toBe('');
    // the button stays usable, the source may just have been unreachable briefly
    expect(document.querySelector('.attribute-reconcile-button').disabled).toBe(false);
  });

  it('names a failing request and submits nothing', async () => {
    const submit = fixture();
    global.fetch = vi.fn(() => Promise.resolve({ok: false, status: 500}));
    await click();
    expect(statusText()).toContain('Spaltenauskunft meldet einen Fehler');
    expect(submit).not.toHaveBeenCalled();
  });

  it('names a rejected request and submits nothing', async () => {
    const submit = fixture();
    vi.spyOn(console, 'error').mockImplementation(() => {});
    global.fetch = vi.fn(() => Promise.reject(new Error('offline')));
    await click();
    expect(statusText()).toContain('Quelle antwortet nicht');
    expect(submit).not.toHaveBeenCalled();
  });

  it('names an answer that carries no column list and submits nothing', async () => {
    const submit = fixture();
    global.fetch = vi.fn(() =>
      Promise.resolve({ok: true, json: () => Promise.resolve({detail: 'nope'})})
    );
    await click();
    expect(statusText()).toContain('Spaltenauskunft meldet einen Fehler');
    expect(submit).not.toHaveBeenCalled();
  });

  it('names an unreadable answer and submits nothing', async () => {
    const submit = fixture();
    vi.spyOn(console, 'error').mockImplementation(() => {});
    global.fetch = vi.fn(() =>
      Promise.resolve({ok: true, json: () => Promise.reject(new SyntaxError('kein JSON'))})
    );
    await click();
    // an unreadable answer is a fault of the column information, not a silent source
    expect(statusText()).toContain('Spaltenauskunft meldet einen Fehler');
    expect(submit).not.toHaveBeenCalled();
  });

  it('tells the three causes apart', async () => {
    const texts = new Set();
    const answers = [
      () => Promise.reject(new Error('offline')),
      () => Promise.resolve({ok: false, status: 500}),
      () => Promise.resolve({ok: true, json: () => Promise.resolve({columns: []})})
    ];
    vi.spyOn(console, 'error').mockImplementation(() => {});
    for (const answer of answers) {
      fixture();
      global.fetch = vi.fn(answer);
      await click();
      texts.add(statusText());
    }
    expect(texts.size).toBe(3);
  });

  it('asks for nothing while schema or table are missing', async () => {
    for (const source of [{schema: ''}, {table: ''}, {db: ''}]) {
      const submit = fixture(source);
      answerWith([{name: 'id', type: 'integer'}]);
      await click();
      expect(statusText()).toContain('angeben');
      expect(global.fetch).not.toHaveBeenCalled();
      expect(submit).not.toHaveBeenCalled();
    }
  });

  it('clears restored field values on load', () => {
    // a marker restored on back navigation would turn the next save into a reconcile
    document.body.innerHTML = `
      <form id="collection_form">
        <div class="attribute-reconcile">
          <button type="button" class="attribute-reconcile-button" data-columns-url="/x/"></button>
          <p class="attribute-reconcile-status"></p>
        </div>
        <input type="hidden" name="reconcile" id="id_reconcile" value="1">
        <input type="hidden" name="reconcile_columns" id="id_reconcile_columns"
               value='[{"name": "id", "type": "integer"}]'>
      </form>`;
    expect(initAttributeReconcile(document)).toBe(true);
    expect(fieldValue('id_reconcile')).toBe('');
    expect(fieldValue('id_reconcile_columns')).toBe('');
  });

  it('leaves the rest of the form untouched', async () => {
    fixture();
    answerWith([{name: 'id', type: 'integer'}]);
    const before = [...document.querySelectorAll('#collection_form [name]')].map((element) => [
      element.name,
      element.value
    ]);
    await click();
    const after = [...document.querySelectorAll('#collection_form [name]')].map((element) => [
      element.name,
      element.value
    ]);
    // only the two carrier fields and the added _continue may differ
    const changed = after.filter(
      ([name, value]) => !before.some(([wasName, wasValue]) => wasName === name && wasValue === value)
    );
    expect(changed.map(([name]) => name).sort()).toEqual([
      '_continue',
      'reconcile',
      'reconcile_columns'
    ]);
  });
});
