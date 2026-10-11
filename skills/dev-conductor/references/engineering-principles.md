# Engineering principles

Reference for humans and for tier-3 design decisions. Agents do not need to load this for
routine work; the `dev-conductor` skill (and the repo's `AGENTS.md`, if any) carry what
must always apply.

Optimize in this order: correctness, simplicity, maintainability, consistency with the
existing codebase, testability, operational safety, clarity.

## DRY, with a caveat
One authoritative definition for domain rules, schemas, validation, permissions, config,
and shared contracts. But similar-looking code is not automatically the same concept.

- Same domain concept **and** same reason to change: strong candidate to abstract.
- Merely looks alike: leave the duplication. A little obvious repetition beats the wrong
  abstraction.
- If an abstraction needs flags or conditionals to serve unrelated cases, or is harder to
  read than the duplication it replaced, reconsider it.

## KISS
Prefer direct control flow, clear data flow, obvious names, explicit dependencies, and
boring proven technology. Avoid needless indirection, factories, plugin systems, event
systems, and clever one-liners.

## YAGNI
Do not build for hypothetical requirements: no extension points without a known consumer,
no config without a current use case, no generic framework for one implementation, no
caching before a demonstrated need, no distributed patterns for local problems. Keep future
change possible, but do not pay for it before it is needed.

## Separation of concerns, cohesion, coupling
Keep responsibilities clear (UI vs business rules vs persistence vs transport). Create
boundaries only where they improve comprehension, testing, change isolation, or security,
not to satisfy a textbook diagram. Prefer small cohesive modules with small interfaces.
Avoid "utils" dumping grounds and coordinators that know everything.

## Single source of truth
Give each important piece of state or rule one canonical owner. Derive instead of
synchronizing copies. If duplication across a boundary is unavoidable, decide which side is
authoritative.

## Least surprise, explicit over clever
Do what another experienced engineer would expect. Follow repo conventions. Avoid hidden
side effects, magic strings, deeply nested ternaries, and obscure language tricks.

## Composition over premature frameworks
Combine small focused units. Do not build an internal platform for one feature. Extract
shared infrastructure only after real reuse or real complexity justifies it.

## Over-engineering check
Before adding any abstraction, service, library, pattern, or layer, answer:

1. What concrete problem does it solve now?
2. Does the repo already have a pattern for this?
3. Can it be solved clearly with less machinery?
4. Is there more than one real consumer?
5. Does it reduce complexity or just move it?
6. What new concepts must future engineers learn?
7. Does it widen the blast radius of future changes?
8. Is it reversible if the assumption is wrong?

Common offenders: single-implementation interfaces, factories that only call constructors,
generic repositories over simple queries, service layers that only proxy, wrapper
hooks/components with no behavior, config for values that never vary, premature queues,
caches, microservices, or state-management frameworks. When unsure, choose the simpler,
reversible option.

Simple is not sloppy. Avoiding over-engineering never excuses missing validation, poor error
handling, unsafe behavior, missing tests, unsafe migrations, or skipped authorization.

## Full-stack changes
Trace the whole path: interaction, frontend state, client/server boundary, validation,
domain logic, authorization, persistence, side effects, response, user-visible outcome.
Consider only the layers that apply, but not the cross-layer consequences you would
otherwise miss.

- Client validation is UX; server validation is enforcement.
- Do not solve a backend problem in the frontend because it is easier.
- Design APIs around application behavior, not around database tables, and do not expose
  internal models directly to the UI.
- Put logic at the narrowest layer that can own the rule correctly.
- Think through error propagation, loading and failure UX, cache invalidation, transaction
  boundaries, concurrency, backward compatibility, and migration safety.
