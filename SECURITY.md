# Security

Creator Workflow Kit is local-first. `doctor`, planning, and the included demo do not authenticate or call a provider.

- Keep keys in environment variables. `config.example.toml` records variable names only.
- Keep OAuth clients and tokens in ignored `credentials/`; use a dedicated token with YouTube's read-only scope.
- Review the exact spoken text before passing `--approve-text`, and source text before `--approve-model-call`.
- Jobs are restricted to `runs/<slug>`. The CLI rejects traversal, absolute paths, duplicate jobs, and unexpected output overwrites.
- Provider failures do not produce a success manifest, so a later retry still needs an explicit command and approval flag.

Report vulnerabilities privately to the repository owner. Do not include credentials, media, account identifiers, or unredacted provider responses in a report.
