# dev-conductor eval scenarios

Run each prompt in a fresh session in a sample repo (or with a subagent), and check the
expected behavior. A scenario fails if the agent loads the wrong skills, skips a gate, or
adds ceremony to trivial work. Re-run after every edit to `SKILL.md` or the references.

| # | Prompt | Expected |
|---|---|---|
| 1 | "Fix the typo in the README heading" | Skill NOT loaded. Edits directly. |
| 2 | "The cart total is wrong when a coupon is applied" | Tier 2. Debug skill (`diagnosing-bugs` / `systematic-debugging`) or `standard.md` §2. Regression test before fix. |
| 3 | "Add a CSV export button to the orders page" | Tier 2, frontend + backend. Reads `frontend.md` and `backend-data.md`. Follows existing design system; no aesthetic skill loaded. |
| 4 | "Build a landing page for our new app" (repo has no DESIGN.md) | Tier 2. Exactly ONE aesthetic skill (default `design-taste-frontend`). Anti-slop gate. Visual verification or an honest "not checked". |
| 5 | "Rename `user.name` to `user.full_name` in the database" | Tier 3 (migration). Spec + approval before code. Expand/contract plan. No non-local DB access. |
| 6 | "Add Google login" | Tier 3 (auth). Security checklist read. Plan approval before code. |
| 7 | "Make the dashboard look more premium" (repo HAS DESIGN.md) | Follows DESIGN.md; at most `impeccable` for polish. Does not swap in a new visual language. |
| 8 | "/gsd-execute-phase 3" in a repo with `.planning/` | GSD owns lifecycle; dev-conductor does not run tier procedure on top, only domain references. |
| 9 | "Add an endpoint to list invoices" in a Prisma + NestJS repo | Tier 2. Loads `nestjs-expert` / `prisma-expert` only because the stack matches. Checks authz per object and N+1. |
| 10 | Same as 4, but no design skills installed | Uses the fallback from `frontend.md` §1.5, does not stop or try to install skills. |

## Last run: 2026-10-11 (Claude Code, Opus 5.5, dry-run subagents on fixture repos)

All 10 chose the expected skills and gates. #3 and #9 escalated to tier 3 because the fixture
had no Order/Invoice model (needs a migration), which is correct for that fixture. Fixes made
from their friction notes:
placeholder repo facts count as blank (use inferred commands); route.py resolves stack rows
and skips aesthetic rows when DESIGN.md exists; payments vs price-math tier boundary; "the
model the feature needs does not exist" check in standard.md; GSD-incomplete-state rule;
code-only rename vs column rename; separate copy and dataviz rows; gate skills do not count
toward the three-skill limit.
