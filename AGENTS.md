# Creator Workflow Kit

This is the portable public starter for the creator workflows explained by Ivan Vydrin.

- Keep the first demo local and free. Paid narration, model calls, avatar generation and YouTube writes require an explicit requested action; setup and diagnostics never invoke them.
- Credentials belong in the user's environment or ignored local credential files. Do not copy any local voice recordings, OAuth tokens, client assets, account IDs or machine-specific configuration from the source workspace.
- Use neutral included examples and documented placeholder configuration. Never describe sample drafts or demo media as a real model-generated result.
- Restrict all job paths to the configured output directory. Never overwrite another job or recursively delete an unchecked path.
- Preserve input text, selected provider/model, durations and source provenance. Review is a real step, and publishing remains a separate user decision.
- The full CompileTheory application remains private unless Ivan explicitly requests its release. Explain its inspected pipeline with diagrams and provide a portable generator; do not advertise a production-equivalent clone.
- Cite and preserve upstream licenses. Prefer an opt-in installer for third-party skills to copying files with uncertain licensing.
- Test the first-run path from a fresh checkout with provider credentials absent. Verify the resulting MP4 with ffprobe and a full decode. Check the local MCP server through its actual stdio protocol.

Use the standard library where it fits. Dependencies must have a concrete purpose and a maintained upstream. Run the meaningful regression tests and the affected end-to-end workflow before reporting completion.
