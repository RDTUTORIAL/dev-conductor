# Changelog

## 1.0.0 - 2026-10-11

First public release.

- `dev-conductor` skill: task tiers (standard / heavy / program), phase routing to installed
  specialist skills with fallbacks, default project rules when a repo has no `AGENTS.md`.
- References: standard and heavy procedures, frontend (one design direction), backend and
  data, security checklist, engineering principles, skill map.
- Scripts: `detect_stack.py` (stack, commands, `DESIGN.md`, GSD, setup warnings),
  `route.py` (resolves the skill map against installed skills and enabled Claude Code
  plugins), `validate.py` (lints the skill).
- Ten agent eval scenarios and script regression tests; CI on Linux, macOS, and Windows.
- Installers for macOS/Linux and Windows; Claude Code plugin and marketplace manifests.
- `install_companions.py` + `companions.json`: installs the 103 companion skills the skill map
  routes to, in four packs, from their original repos via the `skills` CLI, skipping ones
  already installed and filtering stack skills to the repo's stack.
