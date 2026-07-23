# Contributing

Contributions should improve portability, factual fidelity, safety, accessibility, or the usefulness of generated journey documents.

Before opening a pull request:

1. Keep the core skill independent of private systems and company-specific defaults.
2. Add or update an eval for behavior changes.
3. Run the Agent Skills validator against `skills/journey-html`.
4. Run `scripts/validate_html.py` against changed example outputs.
5. Explain any new runtime dependency and why a dependency-free approach is insufficient.
6. Do not commit secrets, private tickets, proprietary screenshots, or unlicensed assets.

Bug reports are most useful when they include a minimal prompt, sanitized input artifacts, the generated output, the agent/client used, and the expected behavior.
