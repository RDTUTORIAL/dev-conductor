# dev-conductor

**One skill that decides how much process a coding task needs, and which of your installed
skills should handle each phase.**

You probably have dozens of agent skills installed: a debugging skill, a TDD skill, three
design skills, a review skill, a migration skill. Left alone, an agent either ignores them or
loads several that fight each other (two design skills producing one incoherent page, two
planners producing two plans). `dev-conductor` is the conductor: it sizes the task, picks
**one** specialist per role, falls back to built-in steps when a specialist is missing, and
keeps the safety gates in place.

Works with **Claude Code** and **Codex** (and any agent that reads `SKILL.md` folders).

## What it does

```
request ──► size it ──► detect repo ──► route each phase ──► verify ──► short report
            tier 1-3    stack, cmds,    to ONE installed      evidence,
                        DESIGN.md,      skill, or fallback    not claims
                        GSD state
```

| Tier | Example | Process |
|---|---|---|
| 1 Trivial | typo, small CSS, copy tweak | Skill is not loaded. Just do it. |
| 2 Standard | bug fix, one page, one endpoint | Understand → short plan → TDD where it fits → verify → diff review |
| 3 Heavy | migration, auth, payments, new subsystem | Spec → **your approval** → vertical slices → security + code review → verify |

Routing examples (from `skills/dev-conductor/references/skill-map.md`):

| Phase | Preferred | Falls back to |
|---|---|---|
| Debug | `diagnosing-bugs` | `systematic-debugging`, then a built-in reproduce → root cause → regression test loop |
| Implement | `tdd` | `test-driven-development`, then red → green → refactor |
| Landing page | `design-taste-frontend` (only if the repo has no `DESIGN.md`) | one type pairing, one accent, one spacing scale |
| ORM | `prisma-expert` / `drizzle-orm-expert` | only the one your repo actually uses |
| Migration | `database-migration` | expand → migrate → contract, local first |
| Review | `code-review` | `requesting-code-review`, then a self-review checklist |

Rules it enforces: one skill per role, load per phase not up front, stack skills only on a
stack match, the repo's own conventions beat every skill, and it never installs anything or
crosses an approval gate on its own.

## Install

**Claude Code (plugin):**

```
/plugin marketplace add RDTUTORIAL/dev-conductor
/plugin install dev-conductor@dev-conductor
```

**Any agent, with the `skills` CLI:**

```bash
npx skills add RDTUTORIAL/dev-conductor
```

**Manual (macOS / Linux):**

```bash
git clone https://github.com/RDTUTORIAL/dev-conductor.git
cd dev-conductor
./install.sh                     # ~/.claude/skills and ~/.agents/skills
./install.sh --claude            # Claude Code only
./install.sh --project ~/code/app --agents-md   # one project, plus the AGENTS.md template
```

**Manual (Windows, PowerShell):**

```powershell
git clone https://github.com/RDTUTORIAL/dev-conductor.git
cd dev-conductor
.\install.ps1                    # add -Agent claude|codex, -Project <dir>, -AgentsMd
```

Restart your agent session afterwards.

### Starting from zero: install the companion skills too

`dev-conductor` works alone, but it shines with specialists to route to. One command installs
them from their original repos using the [`skills` CLI](https://skills.sh) (needs Node.js):

```bash
./install.sh --with-companions                 # core pack (asks before installing)
./install.sh --with-companions all             # every pack
./install.sh --project ~/code/app --with-companions all   # project scope; stack skills only for that repo's stack
```

```powershell
.\install.ps1 -WithCompanions core,frontend
```

Or run it on its own: `python3 install_companions.py` (interactive), `--list` to see every
skill and source, `--dry-run` to print the commands. Skills you already have are skipped.

| Pack | Skills | What |
|---|---|---|
| `core` | 29 | clarify, plan, debug, TDD, review, verify (Superpowers, Matt Pocock, and others) |
| `frontend` | 30 | design direction, components, accessibility, motion, anti-slop, visual testing |
| `backend` | 24 | API, services, databases, migrations, auth, payments, infra, LLM apps |
| `stacks` | 20 | framework and ORM skills; with `--project`/`--repo`, only the ones your stack uses |

> Third-party skills are instructions your agent follows with its full permissions. The
> installer lists every source and asks before installing; review them first. Each skill
> you install also adds its description to every session's context, so install the packs
> you will use rather than everything.

### Optional: the AGENTS.md template

`templates/AGENTS.md` is a short always-loaded project file: task tiers, safety rules, and a
repo-facts table (install, test, lint, build commands). The skill works without it, using
built-in defaults and the commands it detects, but filling in the repo facts makes it more
reliable. Claude Code reads `CLAUDE.md`; either copy the template there or put
`@AGENTS.md` in your `CLAUDE.md`.

## Companion skills

`dev-conductor` bundles none of these. It uses whichever you have, and falls back when you
have none. Good sets to pair it with:

| Set | Covers | Source |
|---|---|---|
| Superpowers | brainstorming, plans, systematic debugging, TDD, code review, verification | [obra/superpowers](https://github.com/obra/superpowers) |
| Matt Pocock's skills | grill-me, tdd, diagnosing-bugs, to-spec, to-tickets, codebase-design | [mattpocock/skills](https://github.com/mattpocock/skills) |
| UI UX Pro Max | product UI design system, palettes, typography | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| Anti-slop | anti-generic UI and copy gates | [miqdadbadjuber/anti-slop](https://github.com/miqdadbadjuber/anti-slop) |
| frontend-design | frontend design direction | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |

It also routes to many common single skills when present (`impeccable`,
`design-taste-frontend`, `prisma-expert`, `database-migration`, `api-design-principles`,
`stripe-integration`, and others); see the skill map for the full list.

## Helper scripts

Python 3.9+, standard library only, read-only. The skill tells the agent when to run them;
you can also run them yourself from a project root:

```bash
python3 -I path/to/dev-conductor/scripts/detect_stack.py           # stack, commands, DESIGN.md, GSD, setup warnings
python3 -I path/to/dev-conductor/scripts/route.py --agent claude debug review   # which installed skill handles a phase
python3 -I path/to/dev-conductor/scripts/route.py --section frontend            # process | frontend | backend
```

On Windows use `py -3` instead of `python3`. Without Python, the agent reads the skill map by
hand; nothing breaks.

## Layout

```
skills/dev-conductor/
  SKILL.md                    entry point: tiers, routing rules, default project rules
  references/                 standard.md, heavy.md, frontend.md, backend-data.md,
                              security-checklist.md, skill-map.md, engineering-principles.md
  scripts/                    detect_stack.py, route.py, validate.py
  evals/                      scenarios.md (agent evals), test_scripts.py (script tests)
templates/AGENTS.md           optional project file
.claude-plugin/               Claude Code plugin + marketplace manifests
install.sh, install.ps1       manual installers (add --with-companions / -WithCompanions)
install_companions.py         companion skill installer; packs and sources in companions.json
```

## Contributing

The most useful contribution is a better skill map: a row for a phase or stack that is
missing, or a better default. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
