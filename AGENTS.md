# Working on this sample

Keep this a small, runnable Google Meet demo with a local meeting-URL form.

- Use Recall's native ElevenLabs audio integration and hosted ElevenLabs webhook tools.
- Keep exactly five conversational tools: start_screenshare, send_chat_message,
  send_current_page_link, stop_screenshare, and leave_call.
- Addressing the agent as Assistant or elevenlabs demo is a model instruction,
  not an enforced audio filter. Do not promise mute, listening controls, or an avatar.
- Join silently and post the short capabilities introduction in meeting chat.
- Each accepted tool posts chat feedback. Requested messages and links are their
  own feedback. Feedback failures must not undo or repeat the underlying action.
- Display public HTTPS pages without reading or interacting with them. Preserve
  the last accepted page URL when a later request fails. Stop only the screen share.
- Keep the launcher local. Expose only authenticated tool callbacks through the
  HTTPS tunnel; scope an expiring token to the server-owned bot ID for each meeting.
- Keep credentials in the ignored root .env or process environment. Never log
  credentials, callback tokens, request bodies, or meeting content.
- Use the current Recall MCP docs and official ElevenLabs docs to verify behavior.
  Record documentation gaps instead of inventing provider settings.
- Use concrete names, keep related logic together, and review files approaching
  300 lines. Avoid speculative abstractions and extra features.
- Do not add evaluator code, test harnesses, verification instrumentation, or
  reports to this repository. Check behavior externally and report the limits.
- Keep the README focused on one reproducible setup and the five-action demo.
