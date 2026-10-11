#!/usr/bin/env python3
"""Install the companion skills dev-conductor routes to, via the `skills` CLI (npx skills).

Usage:
  python3 install_companions.py                         # interactive: pick packs, confirm
  python3 install_companions.py --packs core,frontend   # these packs
  python3 install_companions.py --all --repo ~/code/app # all packs; stack skills only for that repo
  python3 install_companions.py --list                  # show packs and sources, install nothing
  python3 install_companions.py --dry-run --all         # print the commands only

Options:
  --agent both|claude|codex   which agents get the skills (default: both)
  --project DIR               install into DIR (project scope) instead of user-wide
  --include-installed         reinstall skills that are already present
  --yes                       skip the confirmation prompt

Packs and sources live in companions.json. Third-party skills are instructions your agent
will follow with its full permissions: review the sources before installing.
On Windows use `py -3 install_companions.py`. Needs Node.js (for npx) and network access.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "skills" / "dev-conductor" / "scripts"
AGENT_IDS = {"claude": ["claude-code"], "codex": ["codex"], "both": ["claude-code", "codex"]}


def load_packs():
    return json.loads((ROOT / "companions.json").read_text(encoding="utf-8"))["packs"]


def installed_names(agent):
    sys.path.insert(0, str(SCRIPTS))
    try:
        from route import installed
        return installed("any" if agent == "both" else agent)
    except Exception:
        return set()


def stack_tags(repo):
    sys.path.insert(0, str(SCRIPTS))
    from detect_stack import detect
    return set(detect(Path(repo))["stack"])


def plan(packs, chosen, repo, skip):
    """Return {source: [skills]} for the chosen packs, minus skipped and off-stack skills."""
    tags = stack_tags(repo) if repo else None
    result = {}
    for name in chosen:
        pack = packs[name]
        when = pack.get("when", {})
        for source, skills in pack["sources"].items():
            for skill in skills:
                if skill in skip:
                    continue
                if tags is not None and skill in when and not tags.intersection(when[skill]):
                    continue
                bucket = result.setdefault(source, [])
                if skill not in bucket:
                    bucket.append(skill)
    return result


def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def choose_packs(packs):
    print("Packs:")
    for i, (name, pack) in enumerate(packs.items(), 1):
        count = sum(len(s) for s in pack["sources"].values())
        print(f"  {i}. {name:<9} {count:>3} skills  {pack['description']}")
    answer = ask("Install which? (e.g. 1,2 or 'all'; Enter = core) ")
    if not answer:
        return ["core"]
    if answer == "all":
        return list(packs)
    names = list(packs)
    picked = []
    for part in answer.replace(" ", "").split(","):
        if part.isdigit() and 1 <= int(part) <= len(names):
            picked.append(names[int(part) - 1])
        elif part in packs:
            picked.append(part)
    return picked or ["core"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--packs", help="comma-separated pack names")
    ap.add_argument("--all", action="store_true", help="all packs")
    ap.add_argument("--repo", help="only install stack skills matching this repo")
    ap.add_argument("--agent", choices=list(AGENT_IDS), default="both")
    ap.add_argument("--project", help="install into this project directory instead of user-wide")
    ap.add_argument("--include-installed", action="store_true")
    ap.add_argument("--list", action="store_true", help="show packs and sources only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", "-y", action="store_true")
    args = ap.parse_args()

    packs = load_packs()
    if args.list:
        for name, pack in packs.items():
            print(f"\n[{name}] {pack['description']}")
            for source, skills in pack["sources"].items():
                print(f"  https://github.com/{source}\n    {', '.join(skills)}")
        return 0

    if args.all:
        chosen = list(packs)
    elif args.packs:
        chosen = [p.strip() for p in args.packs.split(",") if p.strip()]
        unknown = [p for p in chosen if p not in packs]
        if unknown:
            print(f"unknown pack(s): {', '.join(unknown)}; choose from {', '.join(packs)}", file=sys.stderr)
            return 2
    elif args.yes or not sys.stdin.isatty():
        chosen = ["core"]
    else:
        chosen = choose_packs(packs)

    skip = set() if args.include_installed or args.project else installed_names(args.agent)
    todo = plan(packs, chosen, args.repo, skip)
    total = sum(len(s) for s in todo.values())
    if total == 0:
        print("Nothing to install: every selected skill is already present.")
        return 0

    print(f"\nWill install {total} skill(s) from {len(todo)} source(s) for: {args.agent}"
          + (f" (project: {args.project})" if args.project else " (user-wide)"))
    for source, skills in todo.items():
        print(f"  github.com/{source}: {', '.join(skills)}")
    if skip and not args.include_installed:
        print(f"  (skipping skills you already have; --include-installed to reinstall)")
    print("\nThese are third-party instructions your agent will follow with its full permissions.")

    npx = shutil.which("npx")
    if not npx and not args.dry_run:
        print("\nnpx not found. Install Node.js (https://nodejs.org), then rerun this script.")
        print("Or install each source by hand with: npx skills add <owner/repo> --skill <names>")
        return 1
    if not args.yes and not args.dry_run and ask("Proceed? [y/N] ") not in ("y", "yes"):
        print("Cancelled.")
        return 1

    failed = []
    for source, skills in todo.items():
        cmd = [npx or "npx", "-y", "skills", "add", source, "-y", "--agent", *AGENT_IDS[args.agent],
               "--skill", *skills]
        if not args.project:
            cmd.insert(5, "-g")
        if os.name == "nt":
            cmd.append("--copy")  # symlinks need admin rights or developer mode on Windows
        print("\n$ " + " ".join(["npx"] + cmd[1:]))
        if args.dry_run:
            continue
        code = subprocess.call(cmd, cwd=args.project or None)
        if code != 0:
            failed.append(source)

    if failed:
        print(f"\nFailed: {', '.join(failed)}. Rerun to retry; already-installed skills are skipped.")
        return 1
    if not args.dry_run:
        print("\nDone. Restart your agent session to load the new skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
