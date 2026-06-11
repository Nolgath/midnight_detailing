# Midnight Detailing — Claude Code Instructions

Premium auto-detailing landing site for the Lisbon market. Django backend, server-rendered
templates. Copy is **Portuguese (pt-PT)**. The public site was reset to a blank page on
2026-06-10 to rebuild toward a new visual direction (see **Design direction** below).

---

## Agent Toolkit

This project is wired to a set of Claude Code tools that extend what I (the agent) can do.
Keep this section accurate — it is the source of truth for what's installed and how to use it.

| Tool | Type | Status | Use it for |
|------|------|--------|------------|
| **claude-mem** | Global plugin | ✅ Active | Persistent cross-session memory. Skills: `/mem-search`, `/make-plan`, `/do`, `/smart-explore`, `/timeline-report`. |
| **superpowers** | Global plugin | Installed via `/plugin` | Engineering discipline: TDD, systematic debugging, code review (request/receive), parallel subagents, git worktrees, plan execution, verification-before-completion. |
| **ui-ux-pro-max** | Global plugin | Installed via `/plugin` | Front-end/design intelligence: 67 styles, 96 palettes, 57 font pairings, charts, stack guidelines (React/Next/Astro/Vue/Svelte/Tailwind/shadcn…). Consult before building UI. |
| **get-shit-done** | Project `.claude/` (commands + agents + hooks) | Installed via `npx get-shit-done-cc` | Spec-driven workflow + context-rot control: `/gsd`, `/new-project`, `/plan-phase`, `/execute-phase`, `/ship`, etc. |
| **awesome-claude-code** | Git submodule → `toolkit/awesome-claude-code` | ✅ Present | Curated catalog of hooks, MCP servers, slash commands, CLAUDE.md examples. Consult when choosing new tooling. |

### Operating guidance
- **Memory**: claude-mem captures context automatically. Project memory also lives at
  `~/.claude/projects/C--Users-TDJ-C-Documents-Projects-Cristian-midnight-detailing/memory/`
  (see `MEMORY.md` index). Update it when learning preferences or decisions.
- **Before building UI**: consult **ui-ux-pro-max** for styles/palettes/font pairings that fit
  the design direction below.
- **For non-trivial features**: use **superpowers** (TDD + verification) and/or **get-shit-done**
  (phased plan → execute → verify → ship). Don't ship unverified.
- **awesome-claude-code** is reference only — browse `toolkit/awesome-claude-code/resources/`
  for hooks/MCPs/commands when we want to add capability.

### Restoring the toolkit on a fresh clone
```bash
git submodule update --init --recursive        # awesome-claude-code
npx get-shit-done-cc@latest                     # re-installs get-shit-done into .claude/
# superpowers + ui-ux-pro-max are GLOBAL plugins (per-machine), installed via /plugin
```

---

## Design direction (target visual)

Reference: a luxury car-detailing landing page provided 2026-06-10. Full spec in project memory
(`memory/design-direction.md`). Summary:

- **Color**: near-black background (~#0A0A0A), white headlines, muted-gray body text. Strictly
  **monochrome** car photography with glossy floor reflections. Subtle dark rounded CTA panels.
- **Type**: bold geometric/grotesque sans for big tight headlines; lighter gray sans for body;
  lowercase link labels with trailing `↗` arrows.
- **Structure**: hero (top-left headline + full-bleed reflected car) → two-column feature list
  with line icons → "Play showreel" video → 3-card monochrome gallery → rounded CTA panel with
  car bleeding off-edge → minimal footer.
- **Mood**: premium, understated, cinematic — "crafted after dark".

---

## Stack notes

- Django app `core` (models, views, forms, emails). URLs in `core/urls.py` (pt-PT slugs:
  `/servicos/`, `/contacto/`).
- Templates in `templates/` (`base.html` + `core/`). Design system CSS at
  `static/css/design-system.css`.
- The home view (`core.views.home`) currently renders a blank white page.
- Deploy: Render Blueprint (`render.yaml`); migrate/seed run in `startCommand`.
