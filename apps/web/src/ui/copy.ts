import type { components } from '../api/schema'

type Code = components['schemas']['ApiErrorCode'] | components['schemas']['DomainReasonCode']

const copy: Partial<Record<Code, string>> = {
  HARD_DEADLINE_MISSED: 'This route arrives after your required time.',
  LOW_POSITIVE_SLACK: 'This route works, but there is little time for delays.',
  SERVICE_CANCELLED: 'This service was cancelled.',
  SERVICE_CUTOFF_MISSED: 'You cannot reach this service before check-in or boarding closes.',
  LOCATION_UNREACHABLE: 'This step starts somewhere you cannot reach from the previous step.',
  CAPACITY_INSUFFICIENT: 'There is not enough stated capacity for this trip.',
  CAPACITY_UNKNOWN: 'Availability is unknown, so this option cannot be confirmed.',
  ACCESSIBILITY_UNKNOWN: 'Accessibility support needs confirmation.',
  CASH_LIMIT_EXCEEDED: 'This option needs more cash than your current limit.',
  EXTRA_COST_LIMIT_EXCEEDED: 'This option exceeds your extra-cost limit.',
  STALE_PLAN: 'This option is based on an older journey. Refresh options to continue.',
  PLAN_EXPIRED: 'This option has expired. Refresh options to continue.',
  VERSION_CONFLICT: 'Your journey changed. Refresh before trying again.',
  EVENT_ID_CONFLICT: 'This delay has already been applied to your journey.',
  ITINERARY_EDIT_INVALID: 'This order cannot work with the connected journey. Adjust the draft and try again.',
  COMPLETED_ACTIVITY_IMMUTABLE: 'Completed journey steps are locked.',
  ACTIVE_ACTIVITY_IMMUTABLE: 'Your current journey step is locked.',
  HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED: 'Confirm that you understand this changes your required plans.',
  INTERNAL_ERROR: 'We couldn’t update your journey. Try again.',
}

export const consumerCopy = (code: string, fallback = 'We couldn’t complete that action. Try again.') => copy[code as Code] ?? fallback
