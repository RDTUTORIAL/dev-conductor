#!/usr/bin/env python3
"""Lint the dev-conductor skill itself. Run after editing SKILL.md or any reference.

Usage: python3 -I validate.py

Checks: frontmatter fields and limits, name matches folder, every referenced
references/*.md, scripts/*.py and evals/*.md file exists, and no reference file is orphaned.
Exits non-zero on errors.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, warnings = [], []


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


skill_md = ROOT / "SKILL.md"
text = skill_md.read_text(encoding="utf-8")
fm = frontmatter(text)
if fm is None:
    errors.append("SKILL.md: missing YAML frontmatter")
    fm = {}
name, desc = fm.get("name", ""), fm.get("description", "")
if name != ROOT.name:
    errors.append(f"name '{name}' does not match folder '{ROOT.name}'")
if not re.fullmatch(r"[a-z0-9-]{1,64}", name or "-" * 65):
    errors.append("name must be 1-64 chars of a-z, 0-9, '-'")
if not desc:
    errors.append("description is empty")
elif len(desc) > 1024:
    errors.append(f"description is {len(desc)} chars (max 1024)")
if "Use " not in desc and "use " not in desc:
    warnings.append("description should say when to use the skill")
body_lines = len(text.splitlines())
if body_lines > 500:
    warnings.append(f"SKILL.md has {body_lines} lines; move detail into references/")

all_text = {p: p.read_text(encoding="utf-8") for p in ROOT.rglob("*.md")}
mentioned = set()
for path, content in all_text.items():
    spans = re.findall(r"`([^`\n]+)`", content)
    refs = [r for span in spans for r in re.findall(r"(?:[\w<>-]+/)*[\w.-]+\.(?:md|py)\b", span)]
    for ref in refs:
        base = ref.split("/")[-1]
        mentioned.add(base)
        hits = list(ROOT.rglob(base))
        if not hits and base not in ("AGENTS.md", "CLAUDE.md", "DESIGN.md", "CONTEXT.md",
                                     "README.md", "SKILL.md"):
            errors.append(f"{path.relative_to(ROOT)}: references missing file '{ref}'")

for p in (ROOT / "references").glob("*.md"):
    if p.name not in mentioned:
        warnings.append(f"references/{p.name} is never mentioned, so the agent will never read it")
for p in (ROOT / "scripts").glob("*.py"):
    if p.name not in mentioned:
        warnings.append(f"scripts/{p.name} is never mentioned in any .md")

for w in warnings:
    print(f"warn:  {w}")
for e in errors:
    print(f"error: {e}")
print(f"{'FAIL' if errors else 'OK'}: {len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
