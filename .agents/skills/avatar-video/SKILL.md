---
name: avatar-video
description: Prepare avatar-video inputs and hand off generation to the official HeyGen MCP after a reviewed script and account choice.
---

Keep the job's reviewed source, spoken script, timing, and intended output in `runs/<slug>/`. Generate local motion graphics and a preview first so a paid avatar request has an approved target.

Use HeyGen through `https://mcp.heygen.com/mcp/v1/` with browser OAuth. Ask the user to select the intended account before requesting generation because accounts and credits are external billing boundaries. Store returned file provenance in the job, then run local QC. This kit does not provide a substitute HeyGen server or upload automation.
