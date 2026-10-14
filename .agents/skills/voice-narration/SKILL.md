---
name: voice-narration
description: Prepare and request reviewed narration through Creator Workflow Kit when the user explicitly approves a provider call.
---

Read the job's `spoken-script.txt` aloud or with the user before a paid call. The supported direct path is `python -m creator_kit tts <slug> --approve-text`; it requires `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in the user's environment and never stores either value.

Use `eleven_multilingual_v2` by default. `--model eleven_v4 --language-code uk` is an option when the selected account and voice support it. Reuse requires the same text, model, language and voice fingerprint. Create a new job for a different request.

For agent integration, prefer the official hosted ElevenLabs MCP at `https://api.elevenlabs.io/v1/mcp` with OAuth. Confirm the account and credit boundary before a paid request.
