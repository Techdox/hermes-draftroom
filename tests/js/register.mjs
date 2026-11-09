// Map the Desktop host's bare imports to local test doubles.
import * as mod from 'node:module'

const stubs = { '@hermes/plugin-sdk': './stubs/sdk.mjs', react: './stubs/react.mjs' }
if (typeof mod.registerHooks === 'function') {
  mod.registerHooks({
    resolve(specifier, context, next) {
      return stubs[specifier] ? { url: new URL(stubs[specifier], import.meta.url).href, shortCircuit: true } : next(specifier, context)
    }
  })
} else {
  mod.register('./hooks.mjs', import.meta.url)  // Node 20.6–22.14.
}
