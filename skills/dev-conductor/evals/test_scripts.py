#!/usr/bin/env python3
"""Regression tests for dev-conductor's scripts. Builds throwaway repos in a temp dir.

Usage: python3 -I evals/test_scripts.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DETECT = SKILL / "scripts" / "detect_stack.py"
ROUTE = SKILL / "scripts" / "route.py"
VALIDATE = SKILL / "scripts" / "validate.py"
failures = []


ENV = dict(os.environ)


def run(script, *args, cwd=None):
    out = subprocess.run([sys.executable, "-I", str(script), *args], cwd=cwd, env=ENV,
                         capture_output=True, text=True, timeout=30)
    return out.returncode, out.stdout + out.stderr


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        failures.append(name)
        if detail:
            print("     " + detail.replace("\n", "\n     ")[:600])


def make_repo(root, deps, extra_files=()):
    root.mkdir(parents=True)
    pkg = {"scripts": {"test": "vitest", "lint": "eslint ."}, "dependencies": deps}
    (root / "package.json").write_text(json.dumps(pkg))
    (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n")
    for rel in extra_files:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("x\n")
    return root


def fake_home(home):
    """A HOME with a few Codex skills and one enabled Claude plugin with nested skills."""
    for name in ["prisma-expert", "drizzle-orm-expert", "design-taste-frontend"]:
        d = home / ".agents" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: x\n---\n")
    claude = home / ".claude"
    nested = claude / "plugins" / "cache" / "mkt" / "plug" / "1.0.0" / "skills" / "engineering" / "diagnosing-bugs"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text("---\nname: x\n---\n")
    off = claude / "plugins" / "cache" / "mkt" / "offplug" / "1.0.0" / "skills" / "tdd"
    off.mkdir(parents=True)
    (off / "SKILL.md").write_text("---\nname: x\n---\n")
    (claude / "settings.json").write_text(json.dumps(
        {"enabledPlugins": {"plug@mkt": True, "offplug@mkt": False}}))
    ENV.update(HOME=str(home), USERPROFILE=str(home), CLAUDE_CONFIG_DIR=str(claude),
               CODEX_HOME=str(home / ".codex"))


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    fake_home(tmp / "home")
    next_repo = make_repo(tmp / "next", {"next": "15", "react": "19", "@prisma/client": "6"},
                          ["prisma/schema.prisma"])
    design_repo = make_repo(tmp / "design", {"next": "15", "react": "19"}, ["DESIGN.md"])
    gsd_repo = make_repo(tmp / "gsd", {"next": "15"}, [".planning/STATE.md"])
    nest_repo = make_repo(tmp / "nest", {"@nestjs/core": "10", "drizzle-orm": "0.30"})

    code, out = run(VALIDATE)
    check("validate.py passes on the skill", code == 0, out)

    code, out = run(DETECT, str(next_repo), "--json")
    facts = json.loads(out) if code == 0 else {}
    check("detect: next + prisma tags", {"nextjs", "prisma"} <= set(facts.get("stack", [])), out)
    check("detect: pnpm commands", facts.get("commands", {}).get("test") == "pnpm test", out)
    check("detect: warns on missing node_modules",
          any("node_modules" in w for w in facts.get("setup_warnings", [])), out)

    code, out = run(DETECT, str(design_repo))
    check("detect: notes DESIGN.md", "DESIGN.md exists" in out, out)
    code, out = run(DETECT, str(gsd_repo))
    check("detect: notes GSD", "GSD owns the lifecycle" in out, out)

    code, out = run(ROUTE, "--repo", str(design_repo), "--section", "frontend")
    check("route: DESIGN.md skips aesthetic rows",
          "Expressive page" in out and "skip: DESIGN.md exists" in out, out)

    code, out = run(ROUTE, "--repo", str(nest_repo), "orm")
    check("route: ORM resolves to drizzle for drizzle repo",
          "drizzle-orm-expert" in out and "prisma-expert" not in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "orm")
    check("route: ORM resolves to prisma for prisma repo",
          "prisma-expert" in out and "drizzle" not in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "orm", "--without", "prisma-expert")
    check("route: --without drops the skill", "prisma-expert" not in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "--agent", "claude", "debug")
    check("route: finds nested skill of an enabled Claude plugin", "diagnosing-bugs" in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "--agent", "claude", "implement behavior")
    check("route: ignores skills of a disabled plugin", "use: tdd" not in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "--agent", "codex", "debug")
    check("route: --agent codex does not see Claude plugins", "diagnosing-bugs" not in out, out)

    code, out = run(ROUTE, "--repo", str(next_repo), "zzz-no-such-row")
    check("route: unknown keyword exits non-zero", code == 1, out)

    code, out = run(ROUTE, "--help")
    check("route: --help prints usage", code == 0 and "Usage" in out, out)

# Only in the published repo: the companion list must cover every skill the map routes to.
companions = SKILL.parent.parent / "companions.json"
if companions.exists():
    import re
    packs = json.loads(companions.read_text(encoding="utf-8"))["packs"]
    listed = {s for p in packs.values() for skills in p["sources"].values() for s in skills}
    mapped = {t.split(":")[-1] for t in re.findall(r"`([a-z0-9][a-z0-9:.-]*)`",
              (SKILL / "references" / "skill-map.md").read_text(encoding="utf-8"))}
    not_skills = {"run", "claude-in-chrome", "security-review", "motion", "dataviz", "transform",
                  "opacity", "prefers-reduced-motion"}
    gaps = sorted(n for n in mapped - listed - not_skills if not n.endswith(".md"))
    check("companions.json covers every skill in skill-map.md", not gaps, f"missing: {gaps}")
    for p in packs.values():
        stray = set(p.get("when", {})) - {s for skills in p["sources"].values() for s in skills}
        check("companions.json 'when' keys are skills in the pack", not stray, f"stray: {sorted(stray)}")

print(f"\n{'FAILED' if failures else 'PASSED'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
