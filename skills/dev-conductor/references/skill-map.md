# Skill map

Pick the first entry that is available in this session. "Fallback" is what to do when none
are installed. Names without a namespace also match namespaced variants
(`superpowers:writing-plans`, `antislop:antislop-ui`).

## Process phases

| Phase | Preferred | Alternatives | Fallback |
|---|---|---|---|
| Clarify an unresolved decision | `grill-with-docs` (repo has `CONTEXT.md`/ADRs) | `grill-me`, `grilling`, `ask-questions-if-underspecified` | Ask the open questions one at a time, most consequential first |
| Explore an idea / shape a design | `brainstorming` | `prototype` (when a throwaway build answers the question faster) | Two or three options with trade-offs, recommend one |
| Domain language, ADRs | `domain-modeling` | `architecture-decision-records` | Add terms to `CONTEXT.md`, decisions to `docs/adr/` |
| Write the spec (tier 3) | `brainstorming` → spec file | `to-spec` (only if an issue tracker is configured) | Template in `heavy.md` §1.3 |
| Break into tasks | `writing-plans` | `to-tickets` (tracker configured) | Vertical slices, each runnable and testable |
| Multi-session program | GSD (`gsd-*`) if `.planning/` exists | `wayfinder` | `docs/specs/<slug>.md` with slices |
| Debug a bug or regression | `diagnosing-bugs` | `systematic-debugging` | `standard.md` §2 |
| Implement behavior | `tdd` | `test-driven-development` | Failing test → minimal code → green → next |
| Implement from an approved spec | `implement` / `executing-plans` | `subagent-driven-development` (many independent tasks) | Slice by slice per `heavy.md` Phase 2 |
| Module boundaries, deepening | `codebase-design` | `improve-codebase-architecture` (only when asked to scan) | `engineering-principles.md` |
| Code review | `code-review` (standards + spec) | `requesting-code-review` | Self-review: correctness, simplicity, repo fit, tests |
| Security review | `security-review` | `cc-skill-security-review`, `security-auditor` | `security-checklist.md` |
| Verify before "done" | `verification-before-completion` | none | Re-read the request; confirm each part with evidence |
| Finish branch / PR | `finishing-a-development-branch` | `create-pr`, `commit` | Only when the user asked to commit or open a PR |

Note on built-ins: in Claude Code, `/code-review` and `/security-review` are user-run commands
that may also appear in the skill list. Suggest them to the user; do the review yourself with
the next installed alternative. In Codex, `code-review` is a loadable skill (Matt Pocock's).

## Frontend

Read `frontend.md` first; it decides which row applies. Choose exactly ONE design direction.

| Need | Preferred | Alternatives | Fallback |
|---|---|---|---|
| Work inside an existing design system | none, follow `DESIGN.md` / tokens / existing screens | `impeccable` for critique and polish only | Copy the nearest existing screen's patterns |
| Product UI (dashboard, admin, SaaS, forms) | `ui-ux-pro-max` | `frontend-design`, `baseline-ui` | Clarity first: hierarchy, spacing scale, states |
| Expressive page (landing, portfolio, marketing) | `design-taste-frontend` | `frontend-design`, `high-end-visual-design`, `minimalist-ui`, `industrial-brutalist-ui` | One clear typographic and color idea, no template look |
| Heavy scroll/GSAP storytelling, user asked for it | `gpt-taste` | none | GSAP docs, respect reduced motion |
| Redesign or upgrade existing UI | `redesign-existing-projects` | `impeccable` | Audit first, then change only what the audit justifies |
| Create a `DESIGN.md` | `design-md` | `stitch-design-taste` | Document tokens, type, spacing, components actually used |
| Components (shadcn, Tailwind) | `shadcn` | `tailwind-design-system`, `tailwind-patterns` | Repo's existing component library |
| Motion | CSS transitions by default | `animejs-animation` (repo uses anime.js), GSAP via `gpt-taste`; no Framer Motion skill installed, use `motion` docs | One motion library at most, honor `prefers-reduced-motion` |
| Motion jank | `fixing-motion-performance` | none | Animate transform/opacity only |
| Anti-slop gate (visuals) | `antislop-ui` | `antislop-human` (interactive), `antislop-layoutmobile` (responsive), `unslop` | `frontend.md` honesty rules |
| Page copy (headlines, CTAs) | `antislop-copywriting` | `copywriting`, `ux-copy` | Real facts from the user only, no invented claims |
| Charts, KPI tiles, dashboards | `data-visualization` | `dataviz` (host built-in), `claude-d3js-skill`, `plotly` | One chart form per question, labeled axes, accessible colors |
| Accessibility | `fixing-accessibility` | `ui-a11y`, `wcag-audit-patterns` | `frontend.md` baseline |
| Framework | `nextjs-best-practices` / `react-best-practices` / `sveltekit` / `astro` / `angular` | match the repo | Repo conventions |
| Visual verification | `webapp-testing` | `playwright-skill`, `claude-in-chrome`, `run` | Tell the user it was not checked visually |

## Backend, API, data

Read `backend-data.md` first. Load a stack skill only when the repo uses that stack.

| Need | Preferred | Alternatives | Fallback |
|---|---|---|---|
| API shape (REST/GraphQL) | `api-design-principles` | `api-patterns`, `graphql-architect` | Design around behavior, not tables |
| Service structure | `backend-dev-guidelines` | `nodejs-backend-patterns`, `cc-skill-backend-patterns` | Repo's existing layering |
| Framework | `nestjs-expert` / `fastapi-pro` / `hono` / `django-pro` / `laravel-expert` / `golang-pro` / `rust-pro` | match the repo | Repo conventions |
| Schema and indexes | `database-design` | `postgres-best-practices`, `postgresql` | `backend-data.md` data section |
| ORM | `prisma-expert` / `drizzle-orm-expert` | match the repo | ORM docs |
| Migrations (always tier 3) | `database-migration` | `database-migrations-sql-migrations` | Expand → migrate → contract, reversible, local first |
| Query performance | `sql-optimization-patterns` | `postgresql-optimization`, `database-optimizer` | `EXPLAIN` before and after |
| Auth | `auth-implementation-patterns` | `clerk-auth`, `nextjs-supabase-auth` | Server-side checks per request + security checklist |
| Payments | `stripe-integration` | `payment-integration` | Idempotent webhooks, signature verification |
| Errors and resilience | `error-handling-patterns` | none | Typed errors, no swallowed exceptions |
| Background jobs, queues | `bullmq-specialist` / `inngest` / `trigger-dev` | match the repo | Idempotent handlers, retries with limits |
| Containers, CI, deploy | `docker-expert`, `github-actions-templates` | `deployment-procedures` | Never deploy without user approval |
| LLM features | `claude-api` | `llm-app-patterns`, `rag-engineer` | Security checklist AI section |
