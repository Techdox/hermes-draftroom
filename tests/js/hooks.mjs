const stubs = { '@hermes/plugin-sdk': './stubs/sdk.mjs', react: './stubs/react.mjs' }
export async function resolve(specifier, context, next) {
  if (stubs[specifier]) return { url: new URL(stubs[specifier], import.meta.url).href, shortCircuit: true }
  return next(specifier, context)
}
