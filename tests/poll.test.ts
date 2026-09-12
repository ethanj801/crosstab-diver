import test from 'node:test';
import assert from 'node:assert/strict';
import { compare, initialState, matches, updateState, visibleRecords } from '../src/poll.ts';
import type { Respondent } from '../src/poll.ts';

const records: Respondent[] = Array.from({ length: 600 }, (_, i) => ({
  id: `record-${i}`, number: i + 1, age: 30, age_group: '30-44',
  race_ethnicity: i < 20 ? 'small' : 'large', education: 'college', sex: 'female',
  preference: i % 2 ? 'R' : 'D', weight: i === 0 ? 3 : 1,
}));
const close = (actual: number | null, expected: number) => assert.ok(actual !== null && Math.abs(actual - expected) < 1e-9);

test('a flip moves a 20-person group by 10 points and the topline by 1/3 point', () => {
  close(compare(records.slice(0, 20), { 'record-0': 'R' }, false).change, -10);
  close(compare(records, { 'record-0': 'R' }, false).change, -200 / 600);
});
test('weighted original and current use the same weights', () => {
  const result = compare(records, { 'record-0': 'R' }, true);
  close(result.original, 200 / 602);
  close(result.current, -400 / 602);
  close(result.change, -600 / 602);
  close(compare(records, {}, true).change, 0);
});
test('no matching respondents is unavailable, not a tie', () => {
  assert.deepEqual(compare([], {}, true), { count: 0, original: null, current: null, change: null });
  close(compare(records, {}, false).current, 0);
});
test('edits survive navigation and weighting; reset includes offscreen records', () => {
  let state = updateState(records, initialState(), { type: 'select', id: 'record-0' });
  state = updateState(records, state, { type: 'preference', value: 'R' });
  assert.equal(visibleRecords(records, state)[0].id, 'record-0');
  state = updateState(records, state, { type: 'page', page: 1 });
  assert.equal(state.selectedId, null);
  state = updateState(records, state, { type: 'select', id: 'record-48' });
  state = updateState(records, state, { type: 'preference', value: 'R' });
  state = updateState(records, state, { type: 'filter', dimension: 'race_ethnicity', value: 'small' });
  assert.equal(state.page, 0);
  assert.equal(state.selectedId, null);
  state = updateState(records, state, { type: 'weighting' });
  assert.deepEqual(state.edits, { 'record-0': 'R', 'record-48': 'R' });
  state = updateState(records, state, { type: 'reset' });
  assert.deepEqual(state.edits, {});
  assert.equal(state.filters.race_ethnicity, 'small');
  assert.equal(state.weighted, true);
});
test('selection survives if still visible, reversal clears changed state', () => {
  let state = updateState(records, initialState(), { type: 'select', id: 'record-0' });
  state = updateState(records, state, { type: 'filter', dimension: 'race_ethnicity', value: 'small' });
  assert.equal(state.selectedId, 'record-0');
  state = updateState(records, state, { type: 'preference', value: 'R' });
  state = updateState(records, state, { type: 'preference', value: 'D' });
  assert.deepEqual(state.edits, {});
});
test('filters intersect and fresh state resets everything', () => {
  const state = initialState();
  assert.ok(matches(records[0], state.filters));
  assert.equal(matches(records[0], { ...state.filters, sex: 'male' }), false);
  assert.deepEqual(state, { filters: { race_ethnicity: '', age_group: '', education: '', sex: '' },
    edits: {}, page: 0, selectedId: null, weighted: false });
});
