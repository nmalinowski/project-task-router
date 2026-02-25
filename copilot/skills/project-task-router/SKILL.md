---
name: project-task-router
description: Route product research and software development work to the right skills and model profile across Codex, Claude Code, and Copilot CLI.
---

## Copilot Compatibility Notes

- `Skill(skill="<name>")` references should be interpreted as invoking named skills in this plugin or installed skill set.
- Use deterministic routing to keep triage reproducible.

# Project Task Router

Use this skill when a task needs triage before execution.

## Routing Domains

1. `market-discovery-validation`
2. `product-strategy-positioning`
3. `architecture-build-planning`
4. `feature-implementation`
5. `ui-ux-frontend`
6. `security-compliance-reliability`
7. `data-analytics-ai`
8. `platform-ops-reliability`

## Router Script

```bash
python skills/project-task-router/scripts/route_task.py --task "your task here" --format markdown
```

Optional skill inventory input:

```bash
python skills/project-task-router/scripts/route_task.py --task "your task here" --installed-skills "skill-a,skill-b"
```

## Operational Rules

- If route is `needs-clarification`, ask focused follow-up questions and rerun routing.
- For close scores, present `alternatives` and ask for confirmation before execution.

## Subagent Workflow

1. Route the request.
2. Spawn review subagent for comprehensive analysis.
3. Spawn remediation subagent after review completes.
4. Auto-fix `low`, `medium`, `high` findings; escalate `critical`.