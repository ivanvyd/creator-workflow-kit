---
name: youtube-channel
description: Read a creator's own YouTube channel through the explicit read-only Creator Workflow Kit OAuth workflow.
---

Create a dedicated token with `python -m creator_kit youtube-auth --credentials <client.json> --token credentials/youtube-readonly-token.json`. The command requests `youtube.readonly` and `yt-analytics.readonly`; do not reuse a token with write permissions.

Use `youtube-report` to save a response inside a job and distinguish returned measurements from interpretation. This starter has no upload, edit, delete, playlist, or publishing command.
