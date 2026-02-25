---
name: project-task-router
description: Routes research and development tasks to the right skill stack and model profile.
---

# Project Task Router Agent

Use when a request is ambiguous or spans multiple domains.

## Workflow

1. Route the task:

```bash
python skills/project-task-router/scripts/route_task.py --task "<request>" --format markdown
```

2. If route is `needs-clarification`, ask follow-up questions and rerun.
3. Present route, confidence, model profile, skills, alternatives, and missing capabilities.
4. Spawn review subagent for comprehensive review across bugs, regressions, security, and tests.
5. After review completion, spawn remediation subagent.
6. Remediation policy:
   - Auto-fix low/medium/high findings
   - Escalate critical findings for explicit approval