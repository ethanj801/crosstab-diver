import { categoryLabel, FILTERS, recordLabel } from '../labels';
import { PAGE_SIZE, preference } from '../poll';
import type { Action, Respondent, State } from '../poll';

type Props = { records: Respondent[]; count: number; state: State; dispatch: (action: Action) => void };

export function Respondents({ records, count, state, dispatch }: Props) {
  const start = count === 0 ? 0 : state.page * PAGE_SIZE + 1;
  const end = Math.min((state.page + 1) * PAGE_SIZE, count);
  return <div className="respondents">
    <div className="people">
      {records.map(record => {
        const current = preference(record, state.edits);
        const changed = current !== record.preference;
        const name = `${recordLabel(record.number)}, ${current}${changed ? ', Changed' : ''}`;
        return <button key={record.id} type="button" data-record={record.id}
          className={`person ${current.toLowerCase()}${changed ? ' changed' : ''}`}
          aria-label={name} title={name} aria-pressed={state.selectedId === record.id}
          onClick={() => dispatch({ type: 'select', id: record.id })}>
          {current}{changed && <span className="changed-mark" aria-hidden="true" />}
        </button>;
      })}
    </div>
    <div className="pagination">
      <span>{start}–{end} of {count}</span>
      <div className="page-actions">
        <button type="button" disabled={state.page === 0} onClick={() => dispatch({ type: 'page', page: state.page - 1 })}>Previous</button>
        <button type="button" disabled={end >= count} onClick={() => dispatch({ type: 'page', page: state.page + 1 })}>Next</button>
      </div>
    </div>
  </div>;
}

export function RespondentDetails({ record, state, dispatch }: {
  record: Respondent | undefined; state: State; dispatch: (action: Action) => void;
}) {
  if (!record) return <div className="inspector inspector-empty" aria-hidden="true" />;
  const current = preference(record, state.edits);
  return <aside className="inspector" aria-labelledby="record-heading">
    <h2 id="record-heading">{recordLabel(record.number)}</h2>
    <dl className="demographics">
      {FILTERS.map(({ dimension, label }) => <div className={`detail-${dimension}`} key={dimension}>
        <dt>{label}</dt><dd>{dimension === 'age_group' ? record.age : categoryLabel(dimension, record[dimension])}</dd>
      </div>)}
    </dl>
    <fieldset className="preference-control">
      <legend>Presidential preference</legend>
      <div className="preference-options">
        {(['D', 'R'] as const).map(value => <label key={value} className={`preference-option ${value.toLowerCase()}`}>
          <input type="radio" name="preference" value={value} checked={current === value}
            onChange={() => dispatch({ type: 'preference', value })} />
          <span>{value}</span>
        </label>)}
      </div>
    </fieldset>
    <div className="original-preference"><span>Original preference</span><strong className={record.preference.toLowerCase()}>{record.preference}</strong></div>
    <div className="weight"><span>Weight</span><strong>{(state.weighted ? record.weight : 1).toFixed(3)}</strong></div>
  </aside>;
}
