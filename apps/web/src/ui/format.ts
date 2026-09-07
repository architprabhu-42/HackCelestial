export const formatINR = (paise: number | null) => paise === null
  ? 'Unknown'
  : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: paise % 100 ? 2 : 0 }).format(paise / 100)

export const formatIST = (value: string | null) => value === null ? 'Time unavailable' : `${new Intl.DateTimeFormat('en-IN', {
  timeZone: 'Asia/Kolkata', hour: 'numeric', minute: '2-digit', hour12: true,
}).format(new Date(value))} IST`

export const formatMargin = (seconds: number) => {
  if (seconds === 0) return 'Arrives exactly by the required time · At risk'
  const late = seconds < 0
  const totalMinutes = Math.ceil(Math.abs(seconds) / 60)
  if (totalMinutes < 1) return `Less than a minute ${late ? 'late' : 'early'}`
  return `${totalMinutes} minutes ${late ? 'late' : 'early'}`
}

export const formatKind = (kind: string) => ({
  fixed_transport: 'Scheduled transport', flexible_transfer: 'Local transfer', processing: 'Station or airport exit',
  hotel_checkin: 'Hotel check-in', commitment: 'Wedding',
}[kind] ?? 'Journey activity')
