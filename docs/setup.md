# Connect your own creator setup

Start with the README's local demo. The steps below add accounts and real inputs when you are ready.

## Agent skills and MCP

Launch Codex or Claude Code from this checkout after bootstrap. Codex discovers `.agents/skills`; bootstrap links that folder into `.claude/skills` for Claude Code. Existing conflicting links are preserved.

Print the local server configuration with the virtual environment's Python:

```powershell
.\.venv\Scripts\python tools\emit_mcp_snippet.py
```

Use the TOML output for Codex and the JSON output for Claude Desktop. Each uses this checkout's Python executable. The helper prints snippets and leaves your client settings unchanged.

For Codex's hosted provider connections:

```text
codex mcp add heygen --url https://mcp.heygen.com/mcp/v1/
codex mcp login heygen
codex mcp add elevenlabs --url https://api.elevenlabs.io/v1/mcp
codex mcp login elevenlabs
codex mcp add openai-developer-docs --url https://developers.openai.com/mcp
```

For Claude Code:

```text
claude mcp add --transport http heygen https://mcp.heygen.com/mcp/v1/
claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp
claude mcp add --transport http openai-developer-docs https://developers.openai.com/mcp
```

Use `/mcp` inside Claude Code to complete provider OAuth. Select your own account and check the available tools before requesting generation. The ElevenLabs hosted connection replaces its deprecated local MCP server.

Sources: [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [HeyGen integrations](https://www.heygen.com/en-gb/integrations), [ElevenLabs hosted MCP](https://elevenlabs.io/docs/eleven-agents/operate/hosted-mcp).

## Narration and a finished video

In ElevenLabs, start with a library voice or create your own clone. Instant cloning recommends 1-2 minutes of clean speech. Professional cloning uses more material, requires verification of your own voice, and recommends at least 30 minutes, preferably 2-3 hours. Follow the account's current consent and plan requirements.

For the direct API commands below, set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in your environment. Get the key and voice ID from your own ElevenLabs dashboard. Keep their values out of source files and Git history.

```powershell
.\.venv\Scripts\python -m creator_kit prepare my-lesson --title "Tools and application code" --source examples\tool-calling-source.md --spoken-script examples\spoken-uk.txt
.\.venv\Scripts\python -m creator_kit tts my-lesson --model eleven_v4 --language-code uk --approve-text
.\.venv\Scripts\python -m creator_kit render my-lesson
.\.venv\Scripts\python -m creator_kit qc runs\my-lesson\demo.mp4
```

Review the spoken script before `tts`; that command consumes your provider's allowance. Rendering uses the measured narration duration and mixes the returned audio into the MP4. The default Multilingual v2 route works without the language flag. Listen to a short test before generating a longer narration; a language setting alone does not guarantee an accent or voice match.

Sources: [ElevenLabs Instant cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/instant-voice-cloning), [Professional cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning), [API quickstart](https://elevenlabs.io/docs/eleven-api/quickstart), [pricing](https://elevenlabs.io/pricing/api).

## Avatar footage

Create a HeyGen avatar from your own continuous speaking footage and the required separate consent recording. The guide recommends 2-5 minutes of footage, with stable framing and consistent lighting. Choose the avatar and Look, then supply the narration you already approved.

The hosted HeyGen MCP uses OAuth linked to your web account. Direct API access has a separate billing route; official skills may select it when `HEYGEN_API_KEY` is present. Check the account and generation quote before calling either route. Save the returned clip and its source in your job, and inspect its lip sync and timing. The kit's included renderer is for coded scenes; avatar editing remains a separate workflow.

Sources: [Digital Twin guide](https://help.heygen.com/en/articles/12089286-create-your-first-digital-twin-video-avatar-with-avatar-iv), [consent guide](https://help.heygen.com/en/articles/12092609-recording-your-consent-video), [HeyGen skills](https://github.com/heygen-com/skills).

## Article and post drafts

Set your own `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_WRITER_DEPLOYMENT` and `AZURE_OPENAI_REVIEWER_DEPLOYMENT`. Select deployments that support the configured Chat Completions request. The default request uses the stable `2024-10-21` API with `max_tokens`; reasoning-model compatibility is not inferred from a deployment's name.

```powershell
.\.venv\Scripts\python -m creator_kit content-draft my-lesson --source examples\tool-calling-source.md --kind article --approve-model-call
```

For a post, prepare a separate job and use `--kind post`. The writer and reviewer make bounded model calls. Inspect the draft, review notes and source provenance before using the text. The kit saves drafts; it does not schedule, email or publish them. [The content diagram](diagrams/content-draft-feedback.mmd) shows where those later decisions sit.

## YouTube access

Create a Google Cloud project, enable YouTube Data API and YouTube Analytics API, configure its OAuth consent screen, and create a desktop OAuth client. Download the client file yourself into the ignored `credentials/` directory. Consent-screen testing and verification requirements depend on the app and users.

```powershell
.\.venv\Scripts\python -m creator_kit youtube-auth --credentials credentials\youtube-client.json --token credentials\youtube-readonly-token.json
.\.venv\Scripts\python -m creator_kit youtube-report my-lesson --token credentials\youtube-readonly-token.json
```

Authorize the intended channel. The dedicated token permits channel data and read-only analytics; an existing token with write scopes is rejected. The starter report returns channel statistics and traffic sources. Chapter editing, Shorts production and uploads need their own implementation and authorization.

Source: [Google's installed-app OAuth guide](https://developers.google.com/youtube/v3/guides/auth/installed-apps).

## Optional local experiments

Keep local model environments separate from this kit's lightweight environment.

- [Coqui TTS](https://github.com/idiap/coqui-ai-TTS) provides local voice tools. Its library code uses MPL-2.0; [XTTS-v2 weights](https://huggingface.co/coqui/XTTS-v2) use the separate Coqui Public Model License. Ukrainian is absent from that model's listed languages. Check the actual model's language and usage terms before choosing it.
- [MuseTalk](https://github.com/TMElyralab/MuseTalk) changes mouth movement in recorded footage. Use your own source footage, compatible GPU environment and the upstream setup. Its dependency models have their own licenses, and its internet test footage is for noncommercial research. Weights and footage are not bundled here.
- [LiveAvatar](https://docs.liveavatar.com/docs/lite-mode/overview) is separate from prerecorded HeyGen video. A Teams camera replacement requires an audio-to-avatar bridge plus video/audio routing and a latency test. This starter does not claim a tested Teams integration.
