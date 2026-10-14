# Creator Workflow Kit

Create short videos, voice narration and article/post drafts with the workflows from Ivan Vydrin's knowledge-sharing session. The included demo renders an animated MP4 locally without provider credentials. Connect your own accounts when you want generated narration, model-written drafts or avatar video.

The article/post generator is a portable starter. The full CompileTheory application remains private.

## First run

Install [Python 3.11 or newer](https://www.python.org/downloads/) and [FFmpeg](https://ffmpeg.org/download.html), with `ffmpeg` and `ffprobe` on PATH. Bootstrap installs the Python packages and Chromium once, so it needs network access.

```powershell
git clone https://github.com/ivanvyd/creator-workflow-kit.git
cd creator-workflow-kit
.\bootstrap.ps1
.\.venv\Scripts\python -m creator_kit demo
.\.venv\Scripts\python -m creator_kit doctor
.\.venv\Scripts\python -m creator_kit qc runs\hello-creator\demo.mp4
```

On macOS/Linux:

```sh
./bootstrap.sh
.venv/bin/python -m creator_kit demo
.venv/bin/python -m creator_kit doctor
.venv/bin/python -m creator_kit qc runs/hello-creator/demo.mp4
```

The `demo` command creates `runs/hello-creator/`: source and spoken script, labelled sample article/post drafts, a seekable HTML scene, timeline, manifest, PNG frames, and a silent 8-second 1920×1080 30 fps H.264 MP4. The sample drafts are template examples. To run another demo, choose a new slug with `--slug my-next-demo`.

Run commands from any working directory after the editable install; repository assets and `runs/` are resolved from the installed checkout.

## Commands

| Command | Effect |
| --- | --- |
| `python -m creator_kit plan` | Shows the review-gated local-first sequence. |
| `python -m creator_kit demo [--slug NAME]` | Creates and renders an 8–12 second local demo. |
| `python -m creator_kit render NAME` | Renders an unrendered local job. |
| `python -m creator_kit qc PATH` | Checks dimensions/rate when supplied by the manifest, progressive H.264/yuv420p, full decode, and intentional silence. |
| `python -m creator_kit doctor` | Checks local prerequisites without logging in or changing configuration. |
| `python -m creator_kit tts NAME --approve-text` | Calls ElevenLabs only after text review. |
| `python -m creator_kit prepare NAME --title TEXT --source FILE --spoken-script FILE` | Creates an unrendered local job from supplied source and spoken script. |
| `python -m creator_kit content-draft NAME --source FILE --kind article --approve-model-call` | Runs bounded writer and reviewer passes, then writes a review-only draft. |
| `python -m creator_kit youtube-auth --credentials FILE --token FILE` | Starts explicit OAuth for a dedicated YouTube read-only token. |
| `python -m creator_kit youtube-report NAME --token FILE` | Saves a read-only channel response in a job. |
| `python -m creator_kit mcp` | Serves local, non-destructive MCP tools over stdio. |

## Accounts, spending, and publishing

`config.example.toml` contains environment-variable names, never secret values. Copy it only if you need local settings. `bootstrap` never calls providers.

- **ElevenLabs narration:** set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`; inspect `spoken-script.txt`, then pass `--approve-text`. The default is `eleven_multilingual_v2`; use `--model eleven_v4 --language-code uk` only when the selected account/voice supports that request. A matching successful manifest and audio file are reused. A failed request writes neither a success manifest nor audio.
- **Content drafts:** set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_WRITER_DEPLOYMENT`, and `AZURE_OPENAI_REVIEWER_DEPLOYMENT`; supply a local source file and `--approve-model-call`. `config.toml` can bound input characters and output tokens and rename the non-secret deployment environment variables. The result is explicitly a draft and is never posted. The manifest records a source hash and environment-variable names, not credentials or prompt responses.
- **YouTube:** supply your own OAuth client and a separate ignored token file. The only exposed scopes are `youtube.readonly` and `yt-analytics.readonly`; the report returns channel metadata plus a traffic-source summary. There are no upload, edit, or delete commands, and the kit does not promise impressions, CTR, or retention data.
- **Avatar video:** connect HeyGen through its official remote MCP URL and browser OAuth. Confirm the selected account and generation quote, then give it your approved narration. HeyGen renders the avatar footage.

See [mcp/catalog.json](mcp/catalog.json) and `python tools/emit_mcp_snippet.py` for snippets that you can add to your own Codex or Claude configuration. The helper never changes global settings.

[The setup guide](docs/setup.md) walks through provider accounts, voice selection, MCP login, a narrated example, article/post drafts and YouTube access. [Included examples](examples) provide a neutral source and Ukrainian speaking text.

## MCP

The bundled local server uses the official Python MCP SDK (`FastMCP`, stdio transport) and exposes only `doctor`, `list_jobs`, `inspect_job`, `prepare_demo`, and `render`. It has no tool that publishes, deletes, uploads, or accesses provider credentials.

```sh
python -m creator_kit mcp
```

The package uses the official MCP SDK's FastMCP 1.x API and bounds the dependency below 2.x.

## Skills and optional upstream references

The repo-local skills live under [.agents/skills](.agents/skills). Codex can read them from the checkout. Bootstrap creates a repo-local `.claude/skills` link for Claude when no conflicting path exists; it does not modify user-level configuration.

`tools/install_upstream_skills.py --list` shows the pinned public references. It installs nothing unless you explicitly select an entry whose license permits it. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) records each reference and its license review. The portable Stop Slop copy carries its upstream MIT license and provenance under `.agents/skills/stop-slop/`.

## Architecture and limits

The diagrams in [docs/diagrams](docs/diagrams) have editable Mermaid sources plus self-contained SVG exports:

- [video pipeline](docs/diagrams/video-pipeline.mmd) / [SVG](docs/diagrams/video-pipeline.svg)
- [accounts and billing](docs/diagrams/provider-account-billing.mmd) / [SVG](docs/diagrams/provider-account-billing.svg)
- [draft/publish feedback](docs/diagrams/content-draft-feedback.mmd) / [SVG](docs/diagrams/content-draft-feedback.svg)
- [MCP boundary](docs/diagrams/mcp-boundary.mmd) / [SVG](docs/diagrams/mcp-boundary.svg)

Technical QC validates the encoded file and full decode. It does not prove a human has watched the complete video at full speed with audio; the included demo is intentionally silent. Review visual flags and final copy before publishing.

## Ukrainian quick start / Швидкий старт українською

1. Запустіть `bootstrap.ps1` у Windows або `./bootstrap.sh` у macOS/Linux.
2. Запустіть `python -m creator_kit demo` — це лише локальний, навмисно беззвучний ролик без ключів і списань.
3. Перевірте `runs/hello-creator/demo.mp4` командою `qc` і перегляньте файл вручну.
4. Лише після перевірки підключайте власний обліковий запис для озвучення, моделі, аватара або YouTube. Публікація завжди залишається окремим ручним рішенням.

## Development

```sh
python -m pytest
python tools/scan_sensitive.py
python -m creator_kit demo --slug smoke --width 320 --height 180 --fps 3 --duration 8
python -m creator_kit qc runs/smoke/demo.mp4
```

CI runs the same offline tests and a small Chromium/FFmpeg smoke render without credentials or provider calls. See [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
