# Contributing

## Adding or changing a skill-map row

`skills/dev-conductor/references/skill-map.md` is a set of Markdown tables that
`scripts/route.py` parses. Each row has four cells:

| Need | Preferred | Alternatives | Fallback |
|---|---|---|---|

- Put skill names in backticks; `route.py` treats every backticked name as a candidate.
- A Preferred cell with no backticked name is a default behavior (for example "CSS
  transitions by default"); alternatives are then shown as optional.
- Writing `match the repo` in Alternatives makes it a stack row: only the skill matching the
  repo's stack is used. Map new stacks in `STACK_SKILLS` (`route.py`) and detect them in
  `detect_stack.py`.
- The Fallback must be something an agent can do with no skill installed.
- Only reference skills that are publicly installable, and keep "one skill per role".

## Before opening a PR

```bash
python3 -I skills/dev-conductor/scripts/validate.py
python3 -I skills/dev-conductor/evals/test_scripts.py
```

If you change `SKILL.md` or a reference, also run the scenarios in
`skills/dev-conductor/evals/scenarios.md` with your agent (fresh session per scenario) and
note the result in the PR. Scripts must stay standard-library Python 3.9+ and read-only.

Keep `SKILL.md` short. Detail belongs in `references/`, which the agent reads only when needed.
