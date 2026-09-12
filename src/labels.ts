import type { Dimension } from './poll';

export const FILTERS: { dimension: Dimension; label: string; options: [string, string][] }[] = [
  { dimension: 'race_ethnicity', label: 'Race / ethnicity', options: [
    ['hispanic', 'Hispanic'], ['nh_white', 'Non-Hispanic White'], ['nh_black', 'Non-Hispanic Black'],
    ['nh_asian', 'Non-Hispanic Asian'], ['nh_other', 'Other non-Hispanic'],
  ] },
  { dimension: 'age_group', label: 'Age', options: [
    ['18-29', '18–29'], ['30-44', '30–44'], ['45-64', '45–64'], ['65+', '65+'],
  ] },
  { dimension: 'education', label: 'Education', options: [
    ['hs_or_less', 'High school or less'], ['some_college_or_associate', 'Some college / associate'],
    ['bachelors_or_higher', 'Bachelor’s or higher'],
  ] },
  { dimension: 'sex', label: 'Sex', options: [['male', 'Male'], ['female', 'Female']] },
];

export function categoryLabel(dimension: Dimension, value: string) {
  return FILTERS.find(f => f.dimension === dimension)!.options.find(([key]) => key === value)![1];
}

export function recordLabel(number: number) { return `Record ${String(number).padStart(3, '0')}`; }
export function direction(value: number | null) {
  return value === null || Math.abs(value) < 0.005 ? '' : value > 0 ? 'd' : 'r';
}
export function marginLabel(value: number | null) {
  if (value === null) return 'N/A';
  if (Math.abs(value) < 1e-9) return 'Tie';
  return `${value > 0 ? 'D' : 'R'} +${Math.abs(value).toFixed(2)}`;
}
export function changeLabel(value: number | null) {
  if (value === null) return 'N/A';
  if (Math.abs(value) < 0.005) return '0.00 pts';
  return `${Math.abs(value).toFixed(2)} pts toward ${value > 0 ? 'D' : 'R'}`;
}
