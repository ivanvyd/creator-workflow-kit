---
name: make-video
description: Create a local reviewable video job and render it with Creator Workflow Kit when a user wants a short creator video.
---

Start with `python -m creator_kit plan`, then create a neutral local demo or a new job from verified source material. Keep source, spoken script, scene, timeline, provider selection, and output in one job directory.

Use the built-in renderer for HTML scenes: it seeks each frame deterministically and produces a local MP4. Run `qc` and inspect the resulting video before calling a provider.

For a short silent motion graphic, read `docs/animations.md` and use the `animate-video` skill. It uses the included project-local HyperFrames example and FFmpeg QC; it does not require a provider render.

Treat narration, avatar rendering, and publishing as separate decisions. Do not claim a provider result, a real voice, a customer, or a metric without supplied evidence.
