#!/usr/bin/env python3
"""Print the facts dev-conductor needs for routing: stack, commands, and context docs.

Usage: python3 -I detect_stack.py [REPO_DIR] [--json]

Read-only. Looks only at manifest and doc files; never runs project code.
"""
import json
import sys
from pathlib import Path

# dependency name (or prefix ending in "/") -> tag used by skill-map.md
JS_TAGS = {
    "next": "nextjs", "react": "react", "vue": "vue", "svelte": "svelte",
    "@sveltejs/kit": "sveltekit", "astro": "astro", "@angular/core": "angular",
    "tailwindcss": "tailwind", "@radix-ui/": "radix", "framer-motion": "motion",
    "motion": "motion", "gsap": "gsap", "animejs": "animejs", "three": "threejs",
    "@nestjs/core": "nestjs", "express": "express", "hono": "hono", "fastify": "fastify",
    "@trpc/server": "trpc", "graphql": "graphql",
    "prisma": "prisma", "@prisma/client": "prisma", "drizzle-orm": "drizzle",
    "typeorm": "typeorm", "sequelize": "sequelize", "mongoose": "mongodb",
    "pg": "postgres", "@supabase/supabase-js": "supabase", "@neondatabase/serverless": "postgres",
    "next-auth": "auth", "@auth/core": "auth", "@clerk/nextjs": "clerk", "better-auth": "auth",
    "stripe": "stripe", "bullmq": "bullmq", "inngest": "inngest",
    "@trigger.dev/sdk": "trigger-dev", "zod": "zod", "ai": "ai-sdk",
    "@anthropic-ai/sdk": "claude-api", "vitest": "vitest", "jest": "jest",
    "@playwright/test": "playwright", "cypress": "cypress", "typescript": "typescript",
}
PY_TAGS = {
    "django": "django", "fastapi": "fastapi", "flask": "flask", "sqlalchemy": "sqlalchemy",
    "alembic": "alembic", "pydantic": "pydantic", "pytest": "pytest", "anthropic": "claude-api",
    "celery": "celery", "stripe": "stripe",
}
FILE_TAGS = {
    "go.mod": "go", "Cargo.toml": "rust", "composer.json": "php", "Gemfile": "ruby",
    "pom.xml": "java", "build.gradle": "java", "build.gradle.kts": "kotlin",
    "Dockerfile": "docker", "docker-compose.yml": "docker", "compose.yaml": "docker",
    "prisma/schema.prisma": "prisma", "drizzle.config.ts": "drizzle",
    "alembic.ini": "alembic", "supabase/config.toml": "supabase",
    "vercel.json": "vercel", "pnpm-workspace.yaml": "monorepo", "turbo.json": "monorepo",
    "nx.json": "monorepo", "lerna.json": "monorepo",
}
CONTEXT = {
    "design_md": ["DESIGN.md", "docs/DESIGN.md", "design.md"],
    "context_md": ["CONTEXT.md", "docs/CONTEXT.md"],
    "adr_dir": ["docs/adr", "docs/adrs", "adr", "docs/decisions"],
    "gsd_planning": [".planning"],
    "specs_dir": ["docs/specs", "docs/plans", "specs"],
    "agents_md": ["AGENTS.md", "CLAUDE.md"],
    "ci": [".github/workflows", ".gitlab-ci.yml", ".circleci"],
}
SCRIPT_KEYS = ["dev", "build", "test", "test:unit", "test:e2e", "lint", "typecheck",
               "type-check", "check", "format", "db:migrate", "migrate"]
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".venv", "venv", "target"}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def js_tags(deps):
    tags = set()
    for dep in deps:
        for key, tag in JS_TAGS.items():
            if dep == key or (key.endswith("/") and dep.startswith(key)):
                tags.add(tag)
    return tags


def package_manager(root):
    for lock, pm in [("pnpm-lock.yaml", "pnpm"), ("bun.lockb", "bun"), ("bun.lock", "bun"),
                     ("yarn.lock", "yarn"), ("package-lock.json", "npm")]:
        if (root / lock).exists():
            return pm
    return "npm"


def find_package_jsons(root, limit=40):
    """Root package.json plus workspace packages (two levels deep is enough for apps/*, packages/*)."""
    found = []
    for pattern in ["package.json", "*/package.json", "*/*/package.json"]:
        for p in sorted(root.glob(pattern)):
            if not SKIP_DIRS.intersection(p.relative_to(root).parts):
                found.append(p)
            if len(found) >= limit:
                return found
    return found


def python_deps(root):
    text = ""
    for name in ["pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile"]:
        p = root / name
        if p.exists():
            try:
                text += p.read_text(encoding="utf-8").lower() + "\n"
            except OSError:
                pass
    return {tag for dep, tag in PY_TAGS.items() if dep in text}, bool(text)


def detect(root):
    root = root.resolve()
    tags, commands, packages = set(), {}, []

    for pj in find_package_jsons(root):
        data = read_json(pj) or {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        tags |= js_tags(deps)
        rel = str(pj.parent.relative_to(root)) or "."
        packages.append(rel)
        if rel == ".":
            pm = package_manager(root)
            run = "npm run" if pm == "npm" else pm
            for key in SCRIPT_KEYS:
                if key in data.get("scripts", {}):
                    commands[key] = f"{run} {key}"
            tags.add("node")

    py_tags, has_py = python_deps(root)
    tags |= py_tags
    if has_py:
        tags.add("python")

    for rel, tag in FILE_TAGS.items():
        if (root / rel).exists():
            tags.add(tag)

    if (root / "Makefile").exists():
        try:
            text = (root / "Makefile").read_text(encoding="utf-8")
            for target in ["test", "lint", "build", "dev", "typecheck", "migrate"]:
                if f"\n{target}:" in "\n" + text and target not in commands:
                    commands[target] = f"make {target}"
        except OSError:
            pass

    context = {}
    for key, candidates in CONTEXT.items():
        hits = [c for c in candidates if (root / c).exists()]
        context[key] = hits[0] if hits else None

    domains = []
    if tags & {"nextjs", "react", "vue", "svelte", "sveltekit", "astro", "angular", "tailwind"}:
        domains.append("frontend")
    if tags & {"nextjs", "nestjs", "express", "hono", "fastify", "trpc", "django", "fastapi",
               "flask", "go", "rust", "php", "ruby", "java"}:
        domains.append("backend")
    if tags & {"prisma", "drizzle", "typeorm", "sequelize", "mongodb", "postgres", "supabase",
               "sqlalchemy", "alembic"}:
        domains.append("database")
    if tags & {"auth", "clerk", "stripe"}:
        domains.append("security-sensitive")

    setup = []
    if (root / "package.json").exists():
        if not (root / "node_modules").exists():
            setup.append("node_modules missing: install needed before checks can run")
        for lock in ["pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lock"]:
            lp = root / lock
            if lp.exists() and lp.stat().st_size == 0:
                setup.append(f"{lock} is empty: install may not reproduce versions")
        if "lint" in commands and not any(root.glob("eslint.config.*")) \
                and not any(root.glob(".eslintrc*")) and not (root / "biome.json").exists():
            setup.append("lint script exists but no ESLint/Biome config found")
    if not (root / ".git").exists():
        setup.append("not a git repository: no diff to review, say so in the report")

    return {
        "root": str(root),
        "setup_warnings": setup,
        "domains": domains,
        "stack": sorted(tags),
        "workspace_packages": packages if len(packages) > 1 else [],
        "commands": commands,
        "context": context,
    }


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    root = Path(args[0]) if args else Path.cwd()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    facts = detect(root)
    if as_json:
        print(json.dumps(facts, indent=2))
        return 0
    print(f"repo:     {facts['root']}")
    print(f"repo has: {', '.join(facts['domains']) or 'unknown'}  (layers present, not the task's scope)")
    print(f"stack:    {', '.join(facts['stack']) or 'unknown'}")
    if facts["workspace_packages"]:
        print(f"packages: {', '.join(facts['workspace_packages'])}  (multi-package: tier 3 if a change spans several)")
    print("commands: " + (", ".join(f"{k}=`{v}`" for k, v in facts["commands"].items()) or "none found; ask or check AGENTS.md")
          + ("  (inferred from manifests; report them as inferred)" if facts["commands"] else ""))
    print("context:  " + ", ".join(f"{k}={v}" for k, v in facts["context"].items() if v) or "context:  none")
    for warning in facts["setup_warnings"]:
        print(f"setup:    {warning}")
    if facts["context"]["gsd_planning"]:
        print("note:     .planning/ exists -> GSD owns the lifecycle")
    if facts["context"]["design_md"]:
        print("note:     DESIGN.md exists -> follow it, no aesthetic skill")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
