import { useReducer } from 'react';
import prepared from '../data/georgia-2020/demo.json';
import { Comparison } from './components/Comparison';
import { Filters } from './components/Filters';
import { Respondents, RespondentDetails } from './components/Respondents';
import { compare, initialState, matches, PAGE_SIZE, updateState } from './poll';
import type { Respondent, State, Action } from './poll';

const records = prepared.respondents as Respondent[];
const reducer = (state: State, action: Action) => updateState(records, state, action);

export default function App() {
  const [state, dispatch] = useReducer(reducer, undefined, initialState);
  const filtered = records.filter(r => matches(r, state.filters));
  const visible = filtered.slice(state.page * PAGE_SIZE, (state.page + 1) * PAGE_SIZE);
  const selected = visible.find(r => r.id === state.selectedId);
  const hasFilters = Object.values(state.filters).some(Boolean);
  return <main className="poll-app">
    <header className="page-header">
      <h1>Poll crosstabs</h1>
      <div className="header-actions">
        <label className="raking-control"><input type="checkbox" role="switch" checked={state.weighted}
          onChange={() => dispatch({ type: 'weighting' })} /><span className="switch-track" aria-hidden="true" /><span>Raking</span></label>
        <button type="button" className="reset" disabled={Object.keys(state.edits).length === 0}
          onClick={() => dispatch({ type: 'reset' })}>Reset preferences</button>
      </div>
    </header>
    <Filters filters={state.filters} dispatch={dispatch} />
    <Comparison whole={compare(records, state.edits, state.weighted)}
      subgroup={hasFilters ? compare(filtered, state.edits, state.weighted) : null} />
    <div className="editor">
      <Respondents records={visible} count={filtered.length} state={state} dispatch={dispatch} />
      <RespondentDetails record={selected} state={state} dispatch={dispatch} />
    </div>
  </main>;
}
