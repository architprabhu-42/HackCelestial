import type { RankingPreset } from '../api/client'

const options: { value: RankingPreset; label: string }[] = [
  { value: 'cheapest', label: 'Lowest cost' }, { value: 'fastest', label: 'Earliest arrival' },
  { value: 'fewest_changes', label: 'Fewest changes' },
]

export function RankingControl({ value, onChange, disabled = false }: { value: RankingPreset; onChange: (value: RankingPreset) => void; disabled?: boolean }) {
  return <fieldset className="ranking-control" disabled={disabled}>
    <legend>Sort recovery options</legend>
    {options.map(option => <button key={option.value} type="button" aria-pressed={value === option.value}
      onClick={() => onChange(option.value)}>{option.label}</button>)}
  </fieldset>
}
