// Minimal public-SDK test double. Tests mutate these objects; no app internals.
const atom = value => {
  const listeners = new Set()
  return { get: () => value, set: next => { value = next; for (const fn of listeners) fn() }, subscribe: fn => { listeners.add(fn); return () => listeners.delete(fn) } }
}
export const host = {
  openWorkspace: () => () => {},
  notify: () => {},
  composer: { submit: () => true },
  state: {
    connectionId: atom('local'),
    profile: atom('default'),
    focusedSessionOwner: atom({ connectionId: 'local', profile: 'default' }),
    focusedStoredSessionId: atom('session-1'),
    focusedSessionId: atom('')
  }
}
export const queryClient = {
  cancelQueries: async () => {}, removeQueries: () => {}, invalidateQueries: async () => {}
}
export const useQuery = () => ({})
export const Button = 'button'
export const Input = 'input'
export const Textarea = 'textarea'
export const COMPOSER_AREAS = { middleware: 'composer.middleware' }
export const PALETTE_AREA = 'palette'
