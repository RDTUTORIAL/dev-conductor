# AGENTS.md

This repo publishes the `dev-conductor` skill. `templates/AGENTS.md` is the project template
users copy; this file is for agents working on this repo.

| Item | Value |
|---|---|
| Stack | Markdown skill + standard-library Python 3.9+ scripts, POSIX sh and PowerShell installers |
| Test | `python3 -I skills/dev-conductor/evals/test_scripts.py` |
| Lint the skill | `python3 -I skills/dev-conductor/scripts/validate.py` |
| Lint installer | `shellcheck install.sh` |
| Layout | `skills/dev-conductor/` (the skill), `templates/`, `.claude-plugin/`, installers at root |

Rules:
- Keep scripts read-only, dependency-free, and working on Linux, macOS, and Windows.
- Keep `SKILL.md` short; detail goes in `references/`.
- After changing `skill-map.md`, run both commands above. After changing `SKILL.md` or a
  reference, also run the scenarios in `skills/dev-conductor/evals/scenarios.md`.
- Update `CHANGELOG.md` and the version in `.claude-plugin/*.json` for releases.
