---
name: animate-video
description: Create a short local HTML motion graphic with HyperFrames and FFmpeg when a user wants AI-assisted animation without a provider render or publication.
---

Use the included `examples/hyperframes-neutral` project as the starting point. It pins HyperFrames and GSAP in the project, keeps the timeline seek-safe, and renders locally. Get the user's explicit approval before any account login, provider call, cloud render, or publication.

Ask the AI to draft a scene specification or edit the included HTML. Keep the result deterministic: one paused GSAP timeline in `window.__timelines`, explicit `data-start` and `data-duration` attributes, no clock/randomness/network fetches, and no remote media unless the user supplies and approves it.

Run `npm ci`, `npm run check`, and `npm run render` from the example directory. Then inspect the MP4 with `npm run qc` and a full `ffmpeg -v error -i renders/neutral-motion.mp4 -f null -` decode. Review the output before any publishing decision.

Do not run `hyperframes init`, `hyperframes skills`, `hyperframes publish`, cloud rendering, or a provider model call for this local workflow. For optional upstream authoring references, use the pinned project-local installer described in `docs/animations.md`.
