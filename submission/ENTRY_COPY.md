# Entry copy

## X post

Attach the approved native demo video to this post. Replace both pending link tokens with real public links; do not post placeholders. The attached video is the demo, so no self-link is needed in its caption.

```text
Draftroom keeps a real Markdown draft beside Hermes chat. Select text, ask for a rewrite, review the diff, then accept or reject. Same agent. You control the file.

My @NousResearch plugin hackathon entry.
Code: <PUBLIC_REPO_URL>
PR: <CATALOG_PR_URL>
```

Programmatically checked: **250 characters** as written, including newlines and placeholders. With both URLs counted as X's 23-character t.co links: **263 weighted characters**, below 280. Recheck the final caption in X before publishing; keep the video under 90 seconds.

## Form links: pending

- Catalog pull request: `<CATALOG_PR_URL>`
- X post containing the demo: `<DEMO_X_POST_URL>`
- Source repository, if requested: `<PUBLIC_REPO_URL>`

Form: https://form.typeform.com/to/FwJLvOln. Submit the two required links once the PR and demo post exist; catalog CI/review may follow.

## Concise form description

Draftroom puts a real Markdown draft beside your existing Hermes conversation. Use `/blog`, select a passage and ask the same agent for a rewrite. Review Original, Suggested and Diff, then Accept or Reject. Only human acceptance applies the proposed edit. Saved Markdown and prior revisions live on the backend. No publishing platform, SEO workflow, second LLM client or core patches.

## What goes beyond a prompt or skill

A native editor and persistent draft library, exact selected-range proposals bound to the saved version, an explicit review/acceptance UI, and atomic, conflict-checked file writes with retained revisions. The bundled skill guides co-writing; the plugin implements the state, review controls and safe saving that a prompt alone cannot supply.

## Truthful verification and assumptions

- **Proven on 0.1.0:** actual native Mac selected-text request → existing Hermes agent → real `blog_draft` proposal → human Accept. The saved Markdown was verified: only the selection changed and the prior revision remained.
- **Verified 0.1.2 candidate:** 177 Python tests, 32 Node controller tests and 20 browser checks passed, including the no-final-newline Diff regression and all seven reviewed findings. Source Doctor/plain validation passed with no warnings. Browser checks used a public-SDK host adapter and controlled fixtures, not a live native model demo; exact package and activation evidence remain distinct.
- **Still pending:** native 0.1.2 recheck and recording, public source/pin and the full dependency-install admission gate. The owned admission attempt could not prepare the independent PM runtime; the serving environment was not changed. No public repository, catalog PR, demo post or form submission is claimed here.
- **Setup:** requires a recent compatible Hermes Desktop SDK, a POSIX backend and the existing configured agent/provider. Backend and local Mac UI halves both need activation; the Desktop-serving process may differ from the gateway.
- **Storage:** “local” means files on the Hermes backend, not automatic Mac filesystem sync or offline inference. Rewrites follow the existing agent's provider settings. Unsaved buffers do not survive an app/plugin reload.
