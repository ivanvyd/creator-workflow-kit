---
name: content-pipeline
description: Produce reviewable content drafts from supplied source material through Creator Workflow Kit without publishing.
---

Start with a user-supplied source file. For a deterministic local draft, keep the source and draft in the job. For a model-assisted draft, review the source and run `python -m creator_kit content-draft <slug> --source <file> --approve-model-call` only after explicit approval.

The output is always a draft. Preserve source hash and provider/model provenance, verify factual claims against the supplied source, and leave scheduling and publication as a separate user decision.
