import { changeLabel, direction, marginLabel } from '../labels';
import type { Comparison as Result } from '../poll';

function MarginTrack({ original, current }: Pick<Result, 'original' | 'current'>) {
  const position = (value: number) => `${(value + 100) / 2}%`;
  return <div className="margin-track" aria-hidden="true">
    <span className="track-half track-r" /><span className="track-half track-d" />
    <span className="tie-line" />
    {original !== null && current !== null && <>
      <span className={`margin-movement ${direction(current - original)}`}
        style={{ transform: `translateX(${position(Math.min(original, current))}) scaleX(${Math.abs(current - original) / 200})` }} />
      <span className="marker marker-original" style={{ left: position(original) }} />
      <span className={`marker marker-current ${direction(current)}`} style={{ left: position(current) }} />
    </>}
  </div>;
}

function ResultRow({ label, result, subgroup = false }: { label: string; result: Result; subgroup?: boolean }) {
  return <div className={`result-row${subgroup ? ' subgroup-result' : ''}`} data-result={subgroup ? 'subgroup' : 'whole'}>
    <div className="result-identity"><h2>{label}</h2><span className="record-count"><strong>{result.count}</strong> records</span></div>
    <MarginTrack original={result.original} current={result.current} />
    <span className={`result-original ${direction(result.original)}`}><span className="sr-only">Original </span>{marginLabel(result.original)}</span>
    <strong className={`result-current ${direction(result.current)}`}><span className="sr-only">Current </span>{marginLabel(result.current)}</strong>
    <strong className={`result-change ${direction(result.change)}`}><span className="sr-only">Change </span>{changeLabel(result.change)}</strong>
  </div>;
}

export function Comparison({ whole, subgroup, subgroupName }: { whole: Result; subgroup: Result | null; subgroupName: string }) {
  return <section className="comparison" aria-label="Margin">
    <div className="comparison-head" aria-hidden="true">
      <span />
      <div className="chart-heading"><span>Margin</span><div className="axis-labels"><span>R +100</span><span>Tie</span><span>D +100</span></div></div>
      <span><i className="legend-original" />Original</span>
      <span><i className="legend-current" />Current</span>
      <span>Change</span>
    </div>
    <div className="results" aria-live="polite" aria-atomic="true">
      <ResultRow label="Whole sample" result={whole} />
      {subgroup ? <ResultRow label={subgroupName} result={subgroup} subgroup /> : <div className="result-placeholder" aria-hidden="true" />}
    </div>
  </section>;
}
