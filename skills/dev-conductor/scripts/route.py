#!/usr/bin/env python3
"""Resolve skill-map.md rows to skills that are actually installed on this machine.

Usage:
  python3 -I route.py                     # every row
  python3 -I route.py debug               # rows whose "Need/Phase" cell matches a keyword
  python3 -I route.py --section frontend   # one section (process | frontend | backend)
  python3 -I route.py --agent claude      # only count skills visible to Claude Code
  python3 -I route.py --agent codex       # only count skills visible to Codex
  python3 -I route.py --repo DIR          # repo to read stack from (default: current dir)
  python3 -I route.py --without a,b       # treat these skills as absent (testing fallbacks)

For each row it prints the first installed skill among Preferred + Alternatives, or the
fallback text when none is installed. Stack-specific rows resolve to the skill matching the
repo's stack (via detect_stack.py), and aesthetic rows are skipped when the repo has a
DESIGN.md. Read-only.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_MAP = HERE.parent / "references" / "skill-map.md"
HOME = Path.home()
CLAUDE_HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR", HOME / ".claude"))
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))

CLAUDE_DIRS = [CLAUDE_HOME / "skills", Path.cwd() / ".claude" / "skills"]
CODEX_DIRS = [HOME / ".agents" / "skills", CODEX_HOME / "skills", Path.cwd() / ".agents" / "skills"]
SECTIONS = {"process": "Process phases", "frontend": "Frontend", "backend": "Backend, API, data"}
# Not skills: built-in commands or tools that skill-map.md mentions by name.
BUILTINS = {"security-review", "code-review", "run", "claude-in-chrome"}
TOKEN = re.compile(r"`([a-z0-9][a-z0-9:.-]*)`")
# detect_stack.py tag -> skills it unlocks in "match the repo" rows.
STACK_SKILLS = {
    "nextjs": ["nextjs-best-practices"], "react": ["react-best-practices"],
    "sveltekit": ["sveltekit"], "astro": ["astro"], "angular": ["angular"],
    "nestjs": ["nestjs-expert"], "fastapi": ["fastapi-pro"], "hono": ["hono"],
    "django": ["django-pro"], "php": ["laravel-expert"], "go": ["golang-pro"],
    "rust": ["rust-pro"], "prisma": ["prisma-expert"], "drizzle": ["drizzle-orm-expert"],
    "bullmq": ["bullmq-specialist"], "inngest": ["inngest"], "trigger-dev": ["trigger-dev"],
}
# Rows that pick a visual direction; DESIGN.md replaces them.
AESTHETIC_ROWS = ("Product UI", "Expressive page", "Heavy scroll", "Create a `DESIGN.md`")


def skill_names(root):
    """Names of skill folders under root, at any depth (plugins nest them in categories)."""
    try:
        return {p.parent.name for p in root.rglob("SKILL.md")}
    except OSError:
        return set()


def claude_plugin_skills():
    """Skills from Claude Code plugins that are enabled in user settings."""
    try:
        settings = json.loads((CLAUDE_HOME / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    names = set()
    for key, enabled in settings.get("enabledPlugins", {}).items():
        if not enabled or "@" not in key:
            continue
        plugin, marketplace = key.split("@", 1)
        for version_dir in (CLAUDE_HOME / "plugins" / "cache" / marketplace / plugin).glob("*"):
            names |= skill_names(version_dir / "skills")
    return names


def installed(agent):
    names = set()
    dirs = []
    if agent in ("claude", "any"):
        dirs += CLAUDE_DIRS
    if agent in ("codex", "any"):
        dirs += CODEX_DIRS
    for d in dirs:
        if d.is_dir():
            names |= {p.name for p in d.iterdir() if (p / "SKILL.md").exists()}
    if agent in ("claude", "any"):
        names |= claude_plugin_skills()
    return names


def parse(text):
    """Yield (section, need, candidates, fallback) for each table row."""
    section = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("Phase", "Need"):
            continue
        need, preferred, alts, fallback = cells[:4]
        candidates = [t.split(":")[-1] for t in TOKEN.findall(preferred + " " + alts)]
        # A preferred cell without a skill name is a default behavior, e.g. "CSS transitions".
        default = None if TOKEN.search(preferred) else preferred
        by_stack = "match the repo" in alts
        yield section, need, candidates, fallback, default, by_stack


def repo_facts(repo):
    sys.path.insert(0, str(HERE))
    try:
        from detect_stack import detect
        return detect(repo)
    except Exception as exc:  # routing still works without stack facts
        print(f"warning: stack detection failed: {exc}", file=sys.stderr)
        return {"stack": [], "context": {}}


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    agent, section, keywords, repo, without = "any", None, [], Path.cwd(), set()
    it = iter(argv)
    for arg in it:
        if arg == "--agent":
            agent = next(it, "any")
        elif arg == "--section":
            section = SECTIONS.get(next(it, ""), None)
        elif arg == "--repo":
            repo = Path(next(it, "."))
        elif arg == "--without":
            without |= set(next(it, "").split(","))
        else:
            keywords.append(arg.lower())

    facts = repo_facts(repo)
    stack_skills = {s for tag in facts["stack"] for s in STACK_SKILLS.get(tag, [])}
    design_md = facts["context"].get("design_md")
    have = installed(agent) - without
    if not have:
        print(f"warning: no skills found for agent={agent}", file=sys.stderr)

    rows = 0
    for sec, need, candidates, fallback, default, by_stack in parse(SKILL_MAP.read_text(encoding="utf-8")):
        if section and sec != section:
            continue
        if keywords and not any(re.search(r"\b" + re.escape(k), need.lower()) for k in keywords):
            continue
        rows += 1
        found = [c for c in candidates if c in have]
        pick = found[0] if found else None
        builtin = next((c for c in candidates if c in BUILTINS), None)
        if design_md and need.startswith(AESTHETIC_ROWS):
            print(f"[{sec}] {need}\n    skip: {design_md} exists, follow it instead")
        elif default:
            optional = f"; optional: {', '.join(found[:3])}" if found else ""
            print(f"[{sec}] {need}\n    default: {default}{optional}")
        elif by_stack:
            match = [c for c in found if c in stack_skills]
            if match:
                print(f"[{sec}] {need}\n    use: {', '.join(match)}  (matches repo stack)")
            else:
                print(f"[{sec}] {need}\n    skip: no installed skill matches this repo's stack")
        elif builtin and candidates[0] == builtin and builtin not in have:
            # Preferred is a user-run command (e.g. /security-review), not a loadable skill.
            alt = f"use: {pick}" if pick else f"fallback: {fallback}"
            print(f"[{sec}] {need}\n    {alt}  (and suggest /{builtin} to the user)")
        elif pick:
            others = [c for c in candidates if c in have and c != pick]
            extra = f"  (also installed: {', '.join(others[:3])})" if others else ""
            print(f"[{sec}] {need}\n    use: {pick}{extra}")
        elif builtin:
            print(f"[{sec}] {need}\n    fallback: {fallback}  (and suggest /{builtin} to the user)")
        else:
            print(f"[{sec}] {need}\n    fallback: {fallback}")
    if rows == 0:
        print("no matching rows; try a broader keyword or --section", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
