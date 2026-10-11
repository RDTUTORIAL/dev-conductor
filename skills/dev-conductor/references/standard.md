# Tier 2: Standard procedure

For bounded work in one area: bug fixes, small features, local refactors.
No written spec and no approval gate unless a real decision is unresolved.

## 1. Understand (keep it quick)

1. Restate the task in one or two lines, including what "done" looks like.
2. Find the relevant code, nearby tests, and one analogous implementation already in the
   repo. Match its conventions.
3. Check whether the behavior already partly exists.
4. Note the blast radius: who calls this, what depends on it, what public interface it touches.
5. Confirm what the task depends on exists: the model, table, route, or component it builds
   on. If it is missing, either it lives elsewhere (ask where) or it must be created; a new
   model or table means a migration, which is tier 3.

If an unresolved decision would change the implementation (API shape, data model, behavior
the user did not specify), ask **one** focused question. Do not guess on those.

## 2. Bugs: find the cause before fixing

Use the debug skill from `skill-map.md` (`diagnosing-bugs`, `systematic-debugging`). Otherwise:

1. Reproduce it. Write down expected vs actual behavior.
2. Gather evidence (logs, a failing test, a minimal repro). Narrow to the failing boundary.
3. Identify the root cause, not the first plausible one.
4. Write a failing regression test where a test boundary exists, then fix, then see it pass.

Do not stack multiple debugging methods without a reason. Bring in more only for flaky,
race-condition, multi-system, or environment-specific failures.

## 3. Features and changes: short plan

Post 3 to 6 bullets in the reply: what changes, where, and how it will be verified. Then
proceed. Do not wait for approval unless step 1 left an open question.

## 4. Implement

- Work in small steps; keep the code runnable and testable between steps.
- Use TDD (`tdd` or `test-driven-development` if installed) when there is a real behavior boundary: business
  logic, validation, parsing, transformations, API behavior, bug fixes. Skip test-first for
  pure visual tweaks, throwaway spikes, and docs. Validation still applies there.
- Follow existing patterns. Do not add abstractions, config, or dependencies for
  hypothetical needs.
- Validate at trust boundaries: server-side validation is the enforcement; client-side is UX.
- If you touch UI, read `frontend.md`; for API or data work, `backend-data.md`. If a security
  trigger applies, read `security-checklist.md`. Pick specialist skills from `skill-map.md`.

## 5. Verify

- During work: run the smallest relevant check (single test file, typecheck on the package).
- Before finishing, run what applies from `AGENTS.md` section 2: tests, typecheck, lint,
  build. Use the strongest check that is practical for the scope.
- For behavior with a UI or runtime component, actually exercise it. A green build does not
  prove the feature works.

## 6. Diff review

Read the final diff and check for: unrelated edits, debug output, commented-out code, dead
code, stray files, accidental API changes, missing tests, new dependencies, and anything
beyond the request. The diff should read as one coherent change.

## 7. Report

Follow `AGENTS.md` section 8. Include "worth addressing later" items you noticed but did
not touch.

## Escalate to Heavy if

Auth, payments, secrets, or migrations turn out to be involved; more than one package is
affected; a public interface changes; or the open design questions keep growing. Say so and
switch to `heavy.md`.
