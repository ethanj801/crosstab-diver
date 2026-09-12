import { FILTERS } from '../labels';
import type { Action, Filters as FilterValues } from '../poll';

export function Filters({ filters, dispatch }: { filters: FilterValues; dispatch: (action: Action) => void }) {
  return <div className="filters">
    {FILTERS.map(({ dimension, label, options }) => <label className={`filter filter-${dimension}`} key={dimension}>
      <span>{label}</span>
      <select value={filters[dimension]} onChange={event => dispatch({ type: 'filter', dimension, value: event.target.value })}>
        <option value="">All</option>
        {options.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
      </select>
    </label>)}
  </div>;
}
