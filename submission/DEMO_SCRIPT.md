# Draftroom: 78-second native demo

**Target:** actual Hermes Desktop on Mac, running the final 0.1.2 backend and Desktop halves. Recording is still pending. One continuous, real-time take, with a real rewrite from the configured Hermes agent. No browser harness, fixture suggestion, sped-up wait or substituted model output.

## One rehearsal, then record

1. Finish the 0.1.2 native recheck first, including the no-final-newline Diff case. Confirm the process serving Desktop has loaded `blog_draft` and `draftroom:blog`; enabling a separate gateway is not enough. Keep installation and private file verification off camera.
2. In a new, neutral native conversation, use `/blog A calmer first draft`. Seed and save the Markdown below through the editor. Rehearse the exact shotlist once: real rewrite, review, human Accept, close/reopen. Privately verify the backend file changed only in the selection and retained its prior revision before using that narration.
3. Restore the sample through the editor, save, and clear any pending proposal. Leave the neutral `/blog` exchange visible with chat and draft side by side. Use **Shift-Cmd-5 → Record Selected Portion**, framing only those panes, with microphone narration. Run the take below and review the exported clip before requesting publication approval.

```markdown
# A calmer first draft

Getting an idea into words is easier when the draft stays beside the conversation.

At the present time, this paragraph is being utilised to demonstrate the process of making a small piece of writing more straightforward and easier to understand.

Keep the rest of this note unchanged.
```

Select only the middle paragraph, **without its terminating newline**. Instruction: `Make this shorter and clearer. Keep the meaning.` The agent supplies the actual replacement; do not prepare one.

## Shotlist and ready-to-speak narration

| Time | Actual native screen action | Narration |
| --- | --- | --- |
| 00:00-00:07 | Start on the saved draft beside its existing Hermes chat. Both are readable immediately. | This is Draftroom: your Markdown draft beside Hermes chat. No copying paragraphs between windows. |
| 00:07-00:15 | Briefly point to the visible `/blog` exchange, Markdown editor and saved state. No setup tour. | I opened this with slash blog. It is already saved as Markdown, not just another chat response. |
| 00:15-00:24 | Select the middle paragraph; enter the instruction; click **Rewrite**. | I only want this paragraph tightened. I select it and ask the same Hermes agent to make it shorter and clearer. |
| 00:24-00:41 | Show the real agent turn/tool activity in the same conversation. Keep the unchanged saved paragraph visible. Let genuine waiting remain on screen. | The rewrite runs in this conversation. While it works, the saved draft stays unchanged. The agent can suggest an edit; it cannot accept one. |
| 00:41-00:53 | Use **Original / Suggested** to compare the original with the still-unchanged editor passage and read the replacement. Click **Diff**. Keep **Accept / Reject** visible. | Here is the suggestion. Original matches the saved passage; Suggested shows the replacement. The Diff makes the change clear. Nothing has been applied. |
| 00:53-01:03 | Actually click **Accept**. Show the changed paragraph, untouched surrounding lines and confirmed saved state. | I click Accept myself. That saves the replacement in the real Markdown file. The rest stays put, and the previous version is retained. |
| 01:03-01:13 | Close the draft pane. Use **Open Draftroom** and its draft list to reopen the saved draft; show the accepted passage. | Now I close the pane and reopen the saved draft. The accepted text is still here. That is persisted Markdown. |
| 01:13-01:18 | Hold on the reopened draft beside chat. | Same conversation, a real draft, and you decide what changes. |

**Timing:** 78 seconds total; 152 spoken words. If the real suggestion is not ready by 00:41, stop and retake after resolving latency. Do not hide a wait, fabricate a result or force an unfinished review into the limit. The exported video must remain **under 90 seconds**.

## Privacy and final take checks

- [ ] Final 0.1.2 build is native-rechecked; the take is not the earlier 0.1.0 acceptance run.
- [ ] Frame out connection/profile identifiers, hostnames, IPs, local paths, draft/session IDs, account details, terminals and unrelated sidebars. No private chats, clipboard popovers or notification banners; enable Do Not Disturb.
- [ ] Only neutral sample content and the real rewrite are visible. No credentials, this preparation chat or private artifact files appear in any frame.
- [ ] Recorded pending proposal leaves the file unchanged; recorded human Accept saves it; recorded reopen shows persistence. Do not narrate a check that failed.
- [ ] Readability, microphone audio, actual exported duration and every frame reviewed. Publication remains a separate approval gate.
