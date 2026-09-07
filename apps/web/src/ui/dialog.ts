import { useEffect, useRef } from 'react'

const focusable = 'button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'

/** Keep the lightweight sheets usable as modal dialogs without a dependency. */
export function useDialogFocus(onClose: () => void) {
  const ref = useRef<HTMLElement>(null)
  useEffect(() => {
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const timer = window.setTimeout(() => ref.current?.querySelector<HTMLElement>('[data-dialog-initial-focus]')?.focus(), 0)
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); onClose(); return }
      if (event.key !== 'Tab') return
      const items = [...(ref.current?.querySelectorAll<HTMLElement>(focusable) ?? [])]
      if (!items.length) return
      const first = items[0], last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => { window.clearTimeout(timer); document.removeEventListener('keydown', onKeyDown); opener?.focus() }
  }, [onClose])
  return ref
}
