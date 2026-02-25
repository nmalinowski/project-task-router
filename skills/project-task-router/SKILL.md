---
name: project-task-router
description: Route product research and software development work to the right skills and model profile across Codex, Claude Code, and Copilot CLI.
---

# Project Task Router

Use this skill when a task needs triage before execution. It maps work to the best domain route, skill stack, and model profile using installed skills from:

- `nmalinowski/groundwork`
- `nmalinowski/agents`
- `nmalinowski/ui-ux-pro-max-skill`

## When To Use

- New request is ambiguous or cross-functional.
- You need robust routing across strategy, engineering, design, security, data, and ops.
- You want deterministic, repeatable skill/model selection across tools.

## Routing Domains

1. `market-discovery-validation`
2. `product-strategy-positioning`
3. `architecture-build-planning`
4. `feature-implementation`
5. `ui-ux-frontend`
6. `security-compliance-reliability`
7. `data-analytics-ai`
8. `platform-ops-reliability`

## Routing Method

1. Classify with weighted token/phrase/regex signals.
2. Apply negative-signal penalties.
3. Select top route, plus alternatives when close.
4. Resolve required/optional capabilities to installed skills (dynamic discovery + alias fallback).
5. If confidence is low or route is `needs-clarification`, ask targeted follow-up questions.

## Model Selection Guidance

- `deep_reasoning`: major ambiguity, high-impact decisions
- `balanced`: normal planning + execution
- `fast_execution`: narrow implementation and cleanup work

## Router Script

```bash
python skills/project-task-router/scripts/route_task.py --task "your task here" --format markdown
```

Optional installed-skill inputs:

```bash
python skills/project-task-router/scripts/route_task.py --task "your task here" --installed-skills "skill-a,skill-b"
python skills/project-task-router/scripts/route_task.py --task "your task here" --installed-skills-file installed-skills.json
```

## Execution Rule

- If task spans multiple domains, sequence discovery/strategy first, then build/design, then assurance.
- If route returns `needs-clarification`, capture missing intent (deliverable, risk, domain) and rerun.

## Subagent Orchestration

1. Route the task.
2. Spawn a review subagent for comprehensive findings.
3. After review completes, spawn a remediation subagent.
4. Remediation policy:
   - Auto-fix `low`, `medium`, `high`
   - Escalate `critical` findings for explicit approval