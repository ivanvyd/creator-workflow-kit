# Contributing

Keep changes portable, local-first, and review-gated. Add a stable offline test for changed behavior, run `python -m pytest`, and inspect the complete diff. Do not add provider keys, OAuth tokens, private media, customer data, or generated `runs/` output.

New provider actions need an explicit approval flag, a provenance record written only after success, and documentation of the account/billing boundary.
