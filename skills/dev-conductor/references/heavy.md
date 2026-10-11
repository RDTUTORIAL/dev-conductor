# Tier 3: Heavy procedure

For new subsystems, architecture or data-model changes, migrations, new external
interfaces, multi-package work, and anything touching auth, payments, PII, or secrets.
Three phases: PLAN, EXECUTE, AUDIT. Code does not start until the plan is approved.

## Phase 1: PLAN

### 1.1 Gather context
- Read the relevant code and tests, plus any architecture docs, ADRs, `CONTEXT.md`, or
  domain docs. Treat them as evidence. If your plan contradicts them, say why explicitly.
- List public interfaces and invariants the change must preserve.

### 1.2 Resolve open decisions
- If architecture or domain docs exist, use `grill-with-docs`; if not, `grill-me` (see
  `skill-map.md` for alternatives).
  If neither is installed, ask the user the unresolved questions directly, one at a time,
  most consequential first.
- Skip this for decisions that are already settled. Do not interrogate for the sake of it.

### 1.3 Write the spec
Use `brainstorming` if installed. Save to `docs/specs/YYYY-MM-DD-<slug>.md` (or the repo's
existing spec location). Scale each section to the task; a short section is fine.

1. **Problem and success criteria**: what must be true when this is done
2. **Current state**: what exists today, with file references
3. **Options considered**: two or three realistic approaches and their trade-offs
4. **Recommendation**: the chosen approach and why
5. **Design**: components, data flow, interfaces, data model
6. **Failure behavior**: what happens on invalid input, dependency failure, partial failure
7. **Security and privacy**: trust boundaries, authorization, data exposure
8. **Test strategy**: what is tested at which level
9. **Migration and rollout**: ordering, backward compatibility, rollback path
10. **Out of scope**: what this deliberately does not do

Run the over-engineering check from `engineering-principles.md` on any new
abstraction, service, library, or layer before it goes into the spec.

### 1.4 Approval gate
Present the spec summary and the recommended approach, and wait for the user's approval.
Do not implement before it.

In non-interactive runs, stop here: write the spec, list the open questions, and end.

## Phase 2: EXECUTE

1. Split the work into vertical slices. Each slice leaves the repo runnable and testable.
2. Load domain skills only for what each slice touches (see `skill-map.md` and `AGENTS.md` section 6).
3. Use TDD (`tdd` or `test-driven-development` if installed) for each behavior with a test boundary:
   failing test, minimum implementation, green, next behavior.
4. Verify each slice as it lands (targeted tests, typecheck). Do not batch all validation
   to the end.
5. Stay inside the approved spec. If a spec assumption turns out wrong, stop, state what
   changed, and update the spec or ask the user. Do not silently drift.
6. For migrations: make them reversible where possible, test on local or throwaway data
   first, and never run against a non-local database without explicit user approval.
7. Do not commit or push unless asked.

## Phase 3: AUDIT

Run these in order and report each result honestly.

1. **Full validation**: tests, typecheck, lint, build, as defined in `AGENTS.md` section 2.
   Add integration or end-to-end tests where the spec called for them.
2. **Runtime check**: exercise the real behavior (run the app, call the endpoint, run the
   migration locally). For UI, follow `frontend.md` §8; for APIs and migrations, `backend-data.md` §6.
3. **Security review**: required when any security trigger applies. Follow
   `security-checklist.md`. Security-sensitive work is not done without it.
4. **Spec conformance**: walk the success criteria and failure-behavior sections of the spec
   and confirm each one against evidence.
5. **Code review**: use the review skill from `skill-map.md` (`code-review`, `requesting-code-review`); otherwise do a self-review
   pass for correctness, simplicity, consistency with repo patterns, and test quality.
6. **Final diff review**: unrelated edits, debug output, dead or commented-out code,
   stray or generated files, unnecessary dependencies, accidental API changes, incomplete
   TODOs, anything outside the spec.
7. **Docs**: update README, API docs, or ADRs that the change made stale.
8. **Verification before completion**: use `verification-before-completion` if installed.
   Otherwise, re-read the original request and confirm every part is met by evidence.

## Report

Follow `AGENTS.md` section 8, and add: deviations from the spec, rollout or rollback notes,
and follow-ups that were deliberately left out.
