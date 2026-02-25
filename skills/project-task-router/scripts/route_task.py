#!/usr/bin/env python3
"""Route a task to recommended skills and model profiles."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Signal:
    pattern: str
    weight: float = 1.0
    kind: str = "token"  # token | phrase | regex


@dataclass(frozen=True)
class DomainConfig:
    name: str
    intent_signals: List[Signal]
    negative_signals: List[Signal]
    required_capabilities: List[str]
    optional_capabilities: List[str]
    model_profile: str


def token(pattern: str, weight: float = 1.0) -> Signal:
    return Signal(pattern=pattern, weight=weight, kind="token")


def phrase(pattern: str, weight: float = 1.2) -> Signal:
    return Signal(pattern=pattern, weight=weight, kind="phrase")


def regex(pattern: str, weight: float = 0.8) -> Signal:
    return Signal(pattern=pattern, weight=weight, kind="regex")


DOMAINS: List[DomainConfig] = [
    DomainConfig(
        name="market-discovery-validation",
        intent_signals=[
            token("research", 1.0),
            token("market", 1.2),
            token("discovery", 1.3),
            token("interview", 1.2),
            token("persona", 1.0),
            token("validate", 1.2),
            phrase("go to market", 1.0),
            token("tam", 1.1),
            token("sam", 1.1),
            token("som", 1.1),
        ],
        negative_signals=[
            token("incident", 1.2),
            token("outage", 1.2),
            token("bug", 0.8),
        ],
        required_capabilities=[
            "discovery-process",
            "discovery-interview-prep",
            "problem-framing-canvas",
        ],
        optional_capabilities=[
            "tam-sam-som-calculator",
            "company-research",
            "competitive-landscape",
            "market-sizing-analysis",
        ],
        model_profile="deep_reasoning",
    ),
    DomainConfig(
        name="product-strategy-positioning",
        intent_signals=[
            token("strategy", 1.3),
            token("positioning", 1.2),
            token("roadmap", 1.2),
            token("pricing", 1.1),
            token("segment", 1.0),
            token("prioritize", 1.0),
            phrase("value proposition", 1.2),
            token("mvp", 1.0),
        ],
        negative_signals=[
            token("endpoint", 1.0),
            token("schema", 1.0),
        ],
        required_capabilities=[
            "positioning-statement",
            "roadmap-planning",
            "prioritization-advisor",
        ],
        optional_capabilities=[
            "recommendation-canvas",
            "opportunity-solution-tree",
            "jobs-to-be-done",
        ],
        model_profile="deep_reasoning",
    ),
    DomainConfig(
        name="architecture-build-planning",
        intent_signals=[
            token("architecture", 1.4),
            token("api", 1.2),
            token("integration", 1.2),
            token("planning", 1.1),
            token("spec", 1.1),
            phrase("task breakdown", 1.0),
            phrase("data model", 1.2),
            token("microservice", 1.2),
            regex(r"\badr\b", 1.0),
        ],
        negative_signals=[
            token("wireframe", 1.2),
            token("mockup", 1.2),
        ],
        required_capabilities=[
            "using-groundwork",
            "architecture",
            "tasks",
        ],
        optional_capabilities=[
            "api-design-principles",
            "design-system-patterns",
            "security-requirement-extraction",
        ],
        model_profile="balanced",
    ),
    DomainConfig(
        name="feature-implementation",
        intent_signals=[
            token("implement", 1.3),
            token("build", 1.1),
            token("code", 1.0),
            token("develop", 1.0),
            token("feature", 1.2),
            token("endpoint", 1.1),
            token("migration", 1.1),
            token("fix", 1.2),
            token("refactor", 1.2),
            token("test", 0.9),
        ],
        negative_signals=[
            token("tam", 1.0),
            token("sam", 1.0),
            token("som", 1.0),
        ],
        required_capabilities=[
            "implement-feature",
            "test-driven-development",
            "execute-task",
        ],
        optional_capabilities=[
            "debugging",
            "code-review-excellence",
            "workflow-patterns",
        ],
        model_profile="fast_execution",
    ),
    DomainConfig(
        name="ui-ux-frontend",
        intent_signals=[
            token("ui", 1.2),
            token("ux", 1.2),
            token("frontend", 1.2),
            token("dashboard", 1.1),
            phrase("design system", 1.2),
            token("accessibility", 1.2),
            token("responsive", 1.0),
            token("component", 1.1),
            token("layout", 1.1),
            token("wireframe", 1.1),
            token("mockup", 1.1),
        ],
        negative_signals=[
            token("hipaa", 1.0),
            token("threat", 1.2),
            token("incident", 1.0),
        ],
        required_capabilities=[
            "ui-ux-pro-max",
            "design-system",
            "product-design",
        ],
        optional_capabilities=[
            "responsive-design",
            "interaction-design",
            "accessibility-compliance",
        ],
        model_profile="balanced",
    ),
    DomainConfig(
        name="security-compliance-reliability",
        intent_signals=[
            token("security", 1.4),
            token("compliance", 1.4),
            token("hipaa", 1.4),
            token("threat", 1.2),
            token("risk", 1.1),
            token("incident", 1.3),
            token("audit", 1.2),
            phrase("soc 2", 1.2),
            token("privacy", 1.2),
            phrase("least privilege", 1.1),
        ],
        negative_signals=[
            token("persona", 1.0),
            token("wireframe", 1.0),
        ],
        required_capabilities=[
            "security-requirement-extraction",
            "stride-analysis-patterns",
            "threat-mitigation-mapping",
        ],
        optional_capabilities=[
            "attack-tree-construction",
            "incident-runbook-templates",
            "slo-implementation",
        ],
        model_profile="deep_reasoning",
    ),
    DomainConfig(
        name="data-analytics-ai",
        intent_signals=[
            token("analytics", 1.3),
            token("dataset", 1.1),
            token("pipeline", 1.1),
            token("model", 1.2),
            token("rag", 1.3),
            token("embedding", 1.2),
            token("vector", 1.2),
            token("evaluation", 1.1),
            token("inference", 1.1),
            token("ml", 1.2),
            token("llm", 1.2),
        ],
        negative_signals=[
            token("on-call", 1.0),
            token("incident", 0.8),
        ],
        required_capabilities=[
            "rag-implementation",
            "llm-evaluation",
            "hybrid-search-implementation",
        ],
        optional_capabilities=[
            "embedding-strategies",
            "vector-index-tuning",
            "ml-pipeline-workflow",
        ],
        model_profile="deep_reasoning",
    ),
    DomainConfig(
        name="platform-ops-reliability",
        intent_signals=[
            token("deployment", 1.2),
            token("ci", 1.0),
            token("cd", 1.0),
            token("on-call", 1.3),
            token("slo", 1.2),
            token("sla", 1.1),
            token("latency", 1.1),
            token("throughput", 1.0),
            token("observability", 1.2),
            token("tracing", 1.1),
            token("prometheus", 1.2),
            token("grafana", 1.2),
            token("runbook", 1.1),
            token("kubernetes", 1.1),
            token("infra", 1.0),
        ],
        negative_signals=[
            token("persona", 1.0),
            token("pricing", 1.0),
        ],
        required_capabilities=[
            "deployment-pipeline-design",
            "slo-implementation",
            "incident-runbook-templates",
        ],
        optional_capabilities=[
            "distributed-tracing",
            "prometheus-configuration",
            "grafana-dashboards",
        ],
        model_profile="balanced",
    ),
]


MODEL_HINTS: Dict[str, Dict[str, str]] = {
    "deep_reasoning": {
        "codex_claude_code": "highest-reasoning model available",
        "copilot_cli": "configured top model + reasoning_effort=high",
    },
    "balanced": {
        "codex_claude_code": "default high-quality model",
        "copilot_cli": "configured default model",
    },
    "fast_execution": {
        "codex_claude_code": "faster/lighter model for narrow tasks",
        "copilot_cli": "configured model with reduced reasoning effort",
    },
}


CAPABILITY_ALIAS_OVERRIDES: Dict[str, List[str]] = {
    "ui-ux-pro-max": ["ui-ux-pro-max", "ui-ux-pro-max-skill", "ui-ux-pro"],
    "design-system": ["design-system", "design-system-patterns"],
    "architecture": ["architecture", "architecture-patterns"],
    "tasks": ["tasks", "task-management", "track-management"],
    "execute-task": ["execute-task", "implement-feature"],
    "incident-runbook-templates": ["incident-runbook-templates", "on-call-handoff-patterns"],
    "slo-implementation": ["slo-implementation", "service-mesh-observability"],
}


ENV_SKILL_KEYS = [
    "ROUTER_INSTALLED_SKILLS",
    "INSTALLED_SKILLS",
    "CODEX_INSTALLED_SKILLS",
    "COPILOT_INSTALLED_SKILLS",
    "CLAUDE_INSTALLED_SKILLS",
]


MIN_ROUTING_SCORE = 1.5
MIN_SINGLE_HIT_SCORE = 1.2


def _dedupe_in_order(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    deduped: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _dedupe_paths_in_order(paths: Iterable[Path]) -> List[Path]:
    seen: Set[str] = set()
    deduped: List[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> Set[str]:
    # Keep hyphenated and slash terms intact (for example, "go-to-market", "ui/ux").
    raw_tokens = re.findall(r"[a-z0-9]+(?:[-/][a-z0-9]+)*", text)
    tokens: Set[str] = set()
    for token_value in raw_tokens:
        tokens.add(token_value)
        if "-" in token_value:
            tokens.update(part for part in token_value.split("-") if part)
        if "/" in token_value:
            tokens.update(part for part in token_value.split("/") if part)
    return tokens


def _split_skill_list(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,\n;]+", text)
    return _dedupe_in_order(normalize(part) for part in parts if part.strip())


def _load_skills_file(path: Path) -> Set[str]:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return set()
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Fall back to delimiter parsing when manifest content is malformed.
            return set(_split_skill_list(content))
        if isinstance(parsed, list):
            return set(normalize(str(item)) for item in parsed if str(item).strip())
        if isinstance(parsed, dict):
            for key in ("skills", "installed_skills"):
                if isinstance(parsed.get(key), list):
                    return set(normalize(str(item)) for item in parsed[key] if str(item).strip())
            return set(_split_skill_list(content))
        if isinstance(parsed, str):
            return set(_split_skill_list(parsed))
    return set(_split_skill_list(content))


def _discovery_candidates() -> List[Path]:
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    home_dir = Path.home()

    candidates = [
        Path("installed-skills.json"),
        Path(".codex/installed-skills.json"),
        Path(".claude/installed-skills.json"),
        Path("copilot/installed-skills.json"),
        home_dir / ".codex" / "installed-skills.json",
        home_dir / ".claude" / "installed-skills.json",
        plugin_root / "installed-skills.json",
        plugin_root / ".codex" / "installed-skills.json",
        plugin_root / ".claude" / "installed-skills.json",
        script_dir / "installed-skills.json",
    ]
    return _dedupe_paths_in_order(candidates)


def minimum_routing_score(hit_count: int) -> float:
    if hit_count <= 1:
        return MIN_SINGLE_HIT_SCORE
    return MIN_ROUTING_SCORE


def discover_installed_skills(
    inline_skills: Optional[str] = None,
    skills_file: Optional[str] = None,
) -> Tuple[Optional[Set[str]], str]:
    if inline_skills is not None:
        return set(_split_skill_list(inline_skills)), "inline"

    if skills_file:
        path = Path(skills_file)
        if path.exists():
            return _load_skills_file(path), str(path)
        return set(), str(path)

    for env_key in ENV_SKILL_KEYS:
        env_value = os.getenv(env_key)
        if env_value:
            return set(_split_skill_list(env_value)), f"env:{env_key}"

    for candidate in _discovery_candidates():
        if candidate.exists():
            return _load_skills_file(candidate), str(candidate)

    return None, "unknown"


def capability_aliases(capability: str) -> List[str]:
    if capability in CAPABILITY_ALIAS_OVERRIDES:
        return CAPABILITY_ALIAS_OVERRIDES[capability]
    return _dedupe_in_order(
        [
            capability,
            capability.replace("-", "_"),
            capability.replace("-", ""),
            capability.replace("-", " "),
        ]
    )


def signal_matches(signal: Signal, normalized_text: str, tokens: Set[str]) -> bool:
    normalized_pattern = normalize(signal.pattern)
    if signal.kind == "phrase":
        phrase_pattern = r"\b" + r"\s+".join(re.escape(part) for part in normalized_pattern.split()) + r"\b"
        return re.search(phrase_pattern, normalized_text) is not None
    if signal.kind == "regex":
        return re.search(signal.pattern, normalized_text) is not None
    return normalized_pattern in tokens


def evaluate_domain(domain: DomainConfig, normalized_text: str, tokens: Set[str]) -> Tuple[float, int]:
    positive_score = 0.0
    positive_hits = 0
    for signal in domain.intent_signals:
        if signal_matches(signal, normalized_text, tokens):
            positive_score += signal.weight
            positive_hits += 1

    negative_score = 0.0
    for signal in domain.negative_signals:
        if signal_matches(signal, normalized_text, tokens):
            negative_score += signal.weight

    return max(0.0, positive_score - negative_score), positive_hits


def score_domains(normalized_text: str) -> List[Tuple[DomainConfig, float, int]]:
    tokens = tokenize(normalized_text)
    return [(domain, *evaluate_domain(domain, normalized_text, tokens)) for domain in DOMAINS]


def resolve_capabilities(
    required_capabilities: List[str],
    optional_capabilities: List[str],
    installed_skills: Optional[Set[str]],
) -> Tuple[List[str], List[str], List[str]]:
    required: List[str] = []
    optional: List[str] = []
    missing: List[str] = []

    for capability in required_capabilities:
        aliases = capability_aliases(capability)
        if installed_skills is None:
            required.append(aliases[0])
            continue
        resolved = next((alias for alias in aliases if alias in installed_skills), None)
        if resolved:
            required.append(resolved)
        else:
            missing.append(capability)

    for capability in optional_capabilities:
        aliases = capability_aliases(capability)
        if installed_skills is None:
            optional.append(aliases[0])
            continue
        resolved = next((alias for alias in aliases if alias in installed_skills), None)
        if resolved:
            optional.append(resolved)

    return _dedupe_in_order(required), _dedupe_in_order([s for s in optional if s not in required]), missing


def downgrade_confidence(confidence: str, levels: int) -> str:
    order = ["low", "medium", "high"]
    index = order.index(confidence)
    return order[max(0, index - max(levels, 0))]


def confidence_from_score(score: float, is_ambiguous: bool, hit_count: int) -> str:
    if score < minimum_routing_score(hit_count):
        return "low"
    if hit_count == 1:
        return "low" if is_ambiguous else "medium"
    if score >= 4.0 and hit_count >= 3 and not is_ambiguous:
        return "high"
    if score >= 2.5:
        return "medium"
    return "low"


def clarification_result(
    text: str,
    scored_domains: List[Tuple[DomainConfig, float, int]],
    model_profile: str = "balanced",
    note: Optional[str] = None,
) -> dict:
    evidence = {domain.name: round(score, 3) for domain, score, _ in scored_domains}
    return {
        "task": text,
        "route": "needs-clarification",
        "confidence": "low",
        "model_profile": model_profile,
        "primary_skills": [],
        "secondary_skills": [],
        "model_hints": MODEL_HINTS[model_profile],
        "alternatives": [domain.name for domain, _, _ in scored_domains],
        "missing_capabilities": [],
        "evidence": evidence,
        "note": note
        or "No route-specific signals matched. Clarify deliverable type, risk level, and domain.",
    }


def to_markdown(result: dict) -> str:
    primary_skills = result["primary_skills"] or ["(none yet)"]
    secondary_skills = result["secondary_skills"] or ["(none yet)"]
    lines = [
        f"Task: {result['task']}",
        f"Route: {result['route']}",
        f"Confidence: {result['confidence']}",
        f"Model profile: {result['model_profile']}",
        "",
        "Primary skills:",
    ]
    lines.extend(f"- {name}" for name in primary_skills)
    lines.append("")
    lines.append("Secondary skills:")
    lines.extend(f"- {name}" for name in secondary_skills)
    lines.append("")
    lines.append("Model hints:")
    lines.append(f"- Codex/Claude Code: {result['model_hints']['codex_claude_code']}")
    lines.append(f"- Copilot CLI: {result['model_hints']['copilot_cli']}")
    missing_capabilities = result.get("missing_capabilities", [])
    if missing_capabilities:
        lines.append("")
        lines.append("Missing capabilities:")
        lines.extend(f"- {name}" for name in missing_capabilities)
    alternatives = result.get("alternatives", [])
    if alternatives:
        lines.append("")
        lines.append("Alternative routes:")
        lines.extend(f"- {name}" for name in alternatives)
    evidence = result.get("evidence", {})
    if evidence:
        lines.append("")
        lines.append("Evidence:")
        for domain_name, score in sorted(evidence.items(), key=lambda item: item[1], reverse=True):
            lines.append(f"- {domain_name}: {score}")
    note = result.get("note")
    if note:
        lines.append("")
        lines.append(f"Note: {note}")
    return "\n".join(lines)


def route_task(
    text: str,
    inline_skills: Optional[str] = None,
    skills_file: Optional[str] = None,
) -> dict:
    normalized = normalize(text)
    scored_domains = score_domains(normalized)
    scored_domains.sort(key=lambda item: item[1], reverse=True)
    best_domain, best_score, best_hit_count = scored_domains[0]
    best_min_score = minimum_routing_score(best_hit_count)

    if best_score < best_min_score:
        return clarification_result(text, scored_domains)

    top_window = max(0.6, best_score * 0.15)
    alternatives = [
        domain.name
        for domain, score, hit_count in scored_domains[1:]
        if best_score - score <= top_window and score >= minimum_routing_score(hit_count)
    ]

    installed_skills, skill_source = discover_installed_skills(
        inline_skills=inline_skills,
        skills_file=skills_file,
    )

    primary_skills, secondary_skills, missing_capabilities = resolve_capabilities(
        required_capabilities=best_domain.required_capabilities,
        optional_capabilities=best_domain.optional_capabilities,
        installed_skills=installed_skills,
    )

    if not primary_skills and installed_skills is not None:
        return clarification_result(
            text,
            scored_domains,
            model_profile=best_domain.model_profile,
            note=(
                "Top route selected but none of its required capabilities are installed. "
                f"Skill source: {skill_source}."
            ),
        )

    confidence = confidence_from_score(
        score=best_score,
        is_ambiguous=bool(alternatives),
        hit_count=best_hit_count,
    )
    if missing_capabilities:
        confidence = downgrade_confidence(confidence, 1)

    note_parts: List[str] = []
    if skill_source != "unknown":
        note_parts.append(f"Skill inventory source: {skill_source}.")
    else:
        note_parts.append("Skill inventory source unknown; using capability aliases as fallback.")
    if missing_capabilities:
        note_parts.append(
            "Some required capabilities were not found in discovered skills; review alternatives "
            "or install missing skills."
        )

    evidence = {domain.name: round(score, 3) for domain, score, _ in scored_domains}

    return {
        "task": text,
        "route": best_domain.name,
        "confidence": confidence,
        "model_profile": best_domain.model_profile,
        "primary_skills": primary_skills,
        "secondary_skills": secondary_skills,
        "model_hints": MODEL_HINTS[best_domain.model_profile],
        "alternatives": alternatives,
        "missing_capabilities": missing_capabilities,
        "evidence": evidence,
        "note": " ".join(note_parts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route task to skills/model profile.")
    parser.add_argument("--task", required=True, help="Task statement to route.")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--installed-skills",
        default=None,
        help="Optional comma-separated installed skills list.",
    )
    parser.add_argument(
        "--installed-skills-file",
        default=None,
        help="Optional path to JSON/text file listing installed skills.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = route_task(
        text=args.task,
        inline_skills=args.installed_skills,
        skills_file=args.installed_skills_file,
    )
    if args.format == "markdown":
        print(to_markdown(result))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
