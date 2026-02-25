<p align="center">
  <img src="docs/logo.svg" alt="Project Task Router Logo" width="120" height="120">
</p>

# Project Task Router

[![Deploy GitHub Pages](https://github.com/nmalinowski/project-task-router/actions/workflows/deploy-pages.yml/badge.svg?branch=main)](https://github.com/nmalinowski/project-task-router/actions/workflows/deploy-pages.yml)

[**Live Router Demo**](https://nmalinowski.github.io/project-task-router/)

Cross-platform task triage plugin for Codex, Claude Code, and Copilot CLI.

It routes incoming work requests to:

- A top domain route
- A recommended skill stack (`primary` + `secondary`)
- A model profile (`deep_reasoning`, `balanced`, `fast_execution`)
- Clarification mode when intent is ambiguous

## Features

- Deterministic weighted router script: `skills/project-task-router/scripts/route_task.py`
- 8-domain routing taxonomy
- Token/phrase/regex signal scoring with negative-signal penalties
- Ambiguity handling with `alternatives`
- Dynamic installed-skill discovery with alias fallback
- Missing-capability detection (`missing_capabilities`)
- Subagent orchestration pattern for review then remediation

## Domain Taxonomy

1. `market-discovery-validation`
2. `product-strategy-positioning`
3. `architecture-build-planning`
4. `feature-implementation`
5. `ui-ux-frontend`
6. `security-compliance-reliability`
7. `data-analytics-ai`
8. `platform-ops-reliability`

## Requirements

- Python 3.9+
- Optional installed skill ecosystem:
  - `nmalinowski/groundwork`
  - `nmalinowski/agents`
  - `nmalinowski/ui-ux-pro-max-skill`

## CLI Usage

Basic routing:

```bash
python skills/project-task-router/scripts/route_task.py --task "Implement HIPAA-compliant audit logging"
```

Markdown output:

```bash
python skills/project-task-router/scripts/route_task.py --task "Plan API architecture" --format markdown
```

Route with explicit installed-skill list:

```bash
python skills/project-task-router/scripts/route_task.py --task "Improve frontend layout" --installed-skills "ui-ux-pro-max,design-system,product-design"
```

Route with installed-skill file:

```bash
python skills/project-task-router/scripts/route_task.py --task "Build RAG pipeline" --installed-skills-file installed-skills.json
```

## Skill Discovery Order

When `--installed-skills` and `--installed-skills-file` are not provided, discovery runs in this order:

1. Environment variables: `ROUTER_INSTALLED_SKILLS`, `INSTALLED_SKILLS`, `CODEX_INSTALLED_SKILLS`, `COPILOT_INSTALLED_SKILLS`, `CLAUDE_INSTALLED_SKILLS`
2. Relative manifests:
   - `installed-skills.json`
   - `.codex/installed-skills.json`
   - `.claude/installed-skills.json`
   - `copilot/installed-skills.json`
3. Home manifests:
   - `~/.codex/installed-skills.json`
   - `~/.claude/installed-skills.json`
4. Plugin-local manifests:
   - `<plugin-root>/installed-skills.json`
   - `<plugin-root>/.codex/installed-skills.json`
   - `<plugin-root>/.claude/installed-skills.json`
   - `<script-dir>/installed-skills.json`

First existing manifest wins.

## Output Fields

- `route`: selected domain or `needs-clarification`
- `confidence`: `low`, `medium`, `high`
- `primary_skills` and `secondary_skills`
- `alternatives`: close competing routes
- `missing_capabilities`: required capability IDs not resolved from known inventory
- `evidence`: domain score map
- `note`: routing/discovery hints

## Subagent Workflow

Use this sequence when executing routed work:

1. Run router and confirm route/model/skills.
2. Spawn review subagent for comprehensive findings (correctness, regressions, security, tests).
3. After review completes, spawn remediation subagent.
4. Remediation policy:
   - Auto-fix `low`, `medium`, `high`
   - Escalate `critical` findings for explicit approval

## Development

Run tests:

```bash
python -m unittest discover -s tests -v
```

## License

MIT (see `plugin.json`).
