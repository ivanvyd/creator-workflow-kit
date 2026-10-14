# AI-assisted local animation

This guide creates a short motion graphic from AI-authored HTML, rendered and inspected on your machine with HyperFrames and FFmpeg.

## Included example

The example at `examples/hyperframes-neutral` is a neutral 4-second, 1920×1080, 30 fps silent motion graphic. It uses a single paused GSAP timeline that HyperFrames seeks deterministically. Install [Node.js 22 or newer](https://nodejs.org/) and [FFmpeg](https://ffmpeg.org/) with `ffmpeg` and `ffprobe` on your PATH.

```sh
cd examples/hyperframes-neutral
npm ci
npm run check
npm run render
npm run qc
ffmpeg -v error -i renders/neutral-motion.mp4 -f null -
```

The committed lockfile keeps `hyperframes@0.8.155` and GSAP inside this example’s `node_modules`. The first local render can download the browser binary used by the CLI. It does not authenticate with a video provider or send the composition to a remote render service.

The output is `examples/hyperframes-neutral/renders/neutral-motion.mp4`. `npm run check` runs HyperFrames lint, runtime, layout, motion, and contrast checks. `npm run qc` reports duration, codec, dimensions, frame rate, frame count, and scan type. The FFmpeg command performs a full decode.

## Prompt for an AI coding agent

Give the agent this prompt after it has read `examples/hyperframes-neutral/index.html`:

```text
Edit only examples/hyperframes-neutral/index.html.
Create a four-second, silent 1920x1080 motion graphic about: [topic].
Use facts supplied in this prompt only. Do not invent people, customers, metrics, integrations, or claims.
Keep one paused GSAP root timeline in window.__timelines, retain explicit data-start and data-duration attributes for every timed element, and use no random values, clocks, fetches, external media, provider calls, publish commands, or preview server.
Use 2-4 clear motion beats: entrance, emphasis, hold, and exit. Keep text readable and inside the canvas.
From `examples/hyperframes-neutral`, run `npm run check` and `npm run render`. Report the output path and any failed check. Do not publish the result.
```

Review the HTML and rendered MP4 before using it in a larger cut. Technical checks do not replace a complete human watch-through.

## Optional upstream authoring references

The repository includes a short `animate-video` skill. If you want the upstream HyperFrames authoring references, copy only the four selected Apache-2.0 skill folders into this repository; the command does not write global agent directories:

```sh
python tools/install_upstream_skills.py --install-hyperframes-skills --destination .agents/skills
```

The installer clones `heygen-com/hyperframes` at `38cfcdd56cdc1a8125a8e68a3604357a23ce819f` into a temporary directory and copies `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, and `hyperframes-cli`. It refuses to overwrite any of those destination directories.

Do not use `hyperframes init` for this guide. Its current CLI can install skills outside the project. Do not run `hyperframes skills`, `hyperframes publish`, cloud rendering, or an account login unless you deliberately choose a separate, authorized workflow.
