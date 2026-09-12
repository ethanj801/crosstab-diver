export type Preference = 'D' | 'R';
export type Dimension = 'race_ethnicity' | 'age_group' | 'education' | 'sex';
export type Respondent = {
  id: string;
  number: number;
  age: number;
  preference: Preference;
  weight: number;
} & Record<Dimension, string>;
export type Filters = Record<Dimension, string>;
export type Edits = Record<string, Preference>;
export const PAGE_SIZE = 48;
export const ALL_FILTERS: Filters = { race_ethnicity: '', age_group: '', education: '', sex: '' };

export function matches(record: Respondent, filters: Filters) {
  return (Object.keys(filters) as Dimension[]).every(dim => !filters[dim] || record[dim] === filters[dim]);
}

export function preference(record: Respondent, edits: Edits): Preference {
  return edits[record.id] ?? record.preference;
}

export function compare(records: Respondent[], edits: Edits, weighted: boolean) {
  if (records.length === 0) return { count: 0, original: null, current: null, change: null };
  let total = 0, original = 0, current = 0;
  for (const record of records) {
    const weight = weighted ? record.weight : 1;
    total += weight;
    original += weight * (record.preference === 'D' ? 1 : -1);
    current += weight * (preference(record, edits) === 'D' ? 1 : -1);
  }
  original = 100 * original / total;
  current = 100 * current / total;
  return { count: records.length, original, current, change: current - original };
}

export type Comparison = ReturnType<typeof compare>;
export type State = {
  filters: Filters;
  edits: Edits;
  weighted: boolean;
  page: number;
  selectedId: string | null;
};
export function initialState(): State {
  return { filters: { ...ALL_FILTERS }, edits: {}, weighted: false, page: 0, selectedId: null };
}
export type Action =
  | { type: 'filter'; dimension: Dimension; value: string }
  | { type: 'page'; page: number }
  | { type: 'select'; id: string }
  | { type: 'preference'; value: Preference }
  | { type: 'weighting' }
  | { type: 'reset' };

export function visibleRecords(records: Respondent[], state: State) {
  return records.filter(r => matches(r, state.filters)).slice(state.page * PAGE_SIZE, (state.page + 1) * PAGE_SIZE);
}

export function updateState(records: Respondent[], state: State, action: Action): State {
  switch (action.type) {
    case 'filter':
    case 'page': {
      const filters = action.type === 'filter'
        ? { ...state.filters, [action.dimension]: action.value } : state.filters;
      const count = records.filter(r => matches(r, filters)).length;
      const lastPage = Math.max(0, Math.ceil(count / PAGE_SIZE) - 1);
      const page = action.type === 'filter' ? 0 : Math.max(0, Math.min(action.page, lastPage));
      const next = { ...state, filters, page };
      if (!visibleRecords(records, next).some(r => r.id === state.selectedId)) next.selectedId = null;
      return next;
    }
    case 'select':
      return visibleRecords(records, state).some(r => r.id === action.id)
        ? { ...state, selectedId: action.id } : state;
    case 'preference': {
      const record = records.find(r => r.id === state.selectedId);
      if (!record) return state;
      const edits = { ...state.edits };
      if (action.value === record.preference) delete edits[record.id];
      else edits[record.id] = action.value;
      return { ...state, edits };
    }
    case 'weighting': return { ...state, weighted: !state.weighted };
    case 'reset': return { ...state, edits: {} };
  }
}
