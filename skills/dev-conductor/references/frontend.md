# Frontend

Read this for any UI work. Scale it: a one-line CSS fix needs a quick look at the affected
screen; a new page needs the whole file.

## 1. Choose the design direction (exactly one)

Walk this in order and stop at the first match:

1. **Repo has `DESIGN.md`, tokens, a component library, or similar existing screens.**
   Follow them. Do not load an aesthetic skill; at most use `impeccable` to critique or
   polish within that system. Never restyle existing UI to taste.
2. **Redesign requested.** `redesign-existing-projects` or `impeccable`: audit first, then
   change what the audit justifies, without breaking behavior.
3. **Product UI** (dashboard, admin, settings, forms, SaaS app). `ui-ux-pro-max` or
   `frontend-design`. Usability and information clarity beat decoration.
4. **Expressive page** (landing, portfolio, marketing, launch). One of
   `design-taste-frontend` (default), `high-end-visual-design`, `minimalist-ui`,
   `industrial-brutalist-ui`, or `gpt-taste` when the user wants heavy GSAP scroll motion.
   If the user named a style, pick the matching one; otherwise pick the default.
5. **No skill available.** Pick one type pairing, one accent color, one spacing scale, and
   apply them consistently.

Stacking two aesthetic skills is the most common way to get incoherent UI. If a second one
seems needed, the first was the wrong pick: replace it, do not add.

If a new project has no design system and will have more than one page, write a short
`DESIGN.md` (`design-md` or `stitch-design-taste`) before building the second page.

## 2. Motion

- Default to CSS transitions. Add a library only when CSS cannot express the motion.
- One motion library per project. Use the one already in `package.json` if present.
- Animate `transform` and `opacity`; respect `prefers-reduced-motion`.
- Jank or stutter: `fixing-motion-performance`.

## 3. Honesty and anti-slop

If `antislop-*` skills are installed, route per `AGENTS.md` §6 and finish with their
delivery gate. Regardless: no invented stats, logos, testimonials, or placeholder marketing
copy presented as real; no decoration without a purpose.

## 4. Accessibility baseline (all UI)

- Semantic HTML: real buttons and links, headings in order, labels tied to inputs.
- Fully keyboard usable with a visible focus state.
- Sufficient contrast; meaning never carried by color alone.
- Meaningful alt text, or empty alt for decorative images.

## 5. States

Check each that applies: loading, empty, error, success, disabled, hover, focus, active.
Forms: validation messages, double-submit prevention, failure recovery.

## 6. Layout and responsiveness

- Check one phone width and one desktop width at minimum.
- No horizontal overflow, broken wrapping, or clipped content with long strings.
- Touch targets usable.

## 7. Data and logic placement

- The UI does not own business rules and is not a security boundary.
- Failed requests have clear error and retry paths; no optimistic UI for actions that
  cannot be rolled back safely.

## 8. Verify

A passing build is not proof the UI is right. Run it and look (`webapp-testing`,
`playwright-skill`, `claude-in-chrome`, or `run`), exercise the interactions, and tell the
user plainly if it could not be checked visually.
