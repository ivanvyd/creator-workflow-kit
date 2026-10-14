# Creator Workflow Kit project guidance

`bootstrap.ps1` or `bootstrap.sh` creates a repo-local `.claude/skills` link to `.agents/skills` when that path is absent. It refuses to replace a different existing path and never edits global Claude settings.

Read `README.md` before running a workflow. Provider calls and publication still require the explicit command flags and user decision described there.
