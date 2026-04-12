import re
import sys
from dataclasses import dataclass


SECTION_ORDER = (
    "Objective:",
    "Constraints:",
    "Proxies:",
    "Failure Surfaces:",
    "Invariant Check:",
    "Minimal Repair:",
    "Final Judgment:",
    "Confidence:",
)

FAILURE_PRIORITY = (
    "Proxy Substitution",
    "Optimization Drift",
    "Exploit Surfaces",
    "Constraint Erosion",
    "Objective Ambiguity Collapse",
)

PROXY_PATTERNS = (
    "metric",
    "metrics",
    "kpi",
    "kpis",
    "engagement",
    "retention",
    "click",
    "clicks",
    "ctr",
    "watch time",
    "time on site",
    "throughput",
    "efficiency",
    "velocity",
    "growth",
    "conversion",
    "score",
    "ranking",
    "rankings",
    "quota",
    "quotas",
    "utilization",
    "time",
    "times",
    "volume",
    "volumes",
    "rate",
    "rates",
    "handling time",
    "discharge time",
    "discharge times",
    "turnaround",
    "latency",
    "speed",
)

CONSTRAINT_CUES = (
    "must",
    "must not",
    "should",
    "should not",
    "cannot",
    "can't",
    "without",
    "while",
    "only",
    "never",
    "preserve",
    "maintain",
    "avoid",
    "limit",
    "bounded",
    "constraint",
    "constraints",
)

OBJECTIVE_CUES = (
    "objective",
    "goal",
    "purpose",
    "aim",
    "intended",
    "meant to",
    "designed to",
    "optimize for",
)

OPTIMIZATION_CUES = (
    "optimize",
    "maximize",
    "minimize",
    "scale",
    "increase",
    "reduce",
    "improve",
    "target",
    "pressure",
    "incentive",
)

PROXY_SIGNAL_CUES = (
    "optimize for",
    "measure success by",
    "maximize",
    "minimize",
    "increase",
    "reduce",
)

BROAD_OBJECTIVE_PATTERNS = (
    "readmission",
    "learning",
    "outcome",
    "outcomes",
    "quality",
    "safety",
    "welfare",
    "accurate",
    "accuracy",
    "integrity",
    "support",
    "preserve",
)

NARROW_PROXY_PATTERNS = (
    "time",
    "times",
    "throughput",
    "volume",
    "volumes",
    "rate",
    "rates",
    "score",
    "scores",
    "ranking",
    "rankings",
    "retention",
    "engagement",
    "efficiency",
    "velocity",
    "utilization",
    "handling time",
    "discharge time",
    "discharge times",
    "turnaround",
    "latency",
    "speed",
)


@dataclass(frozen=True)
class AuditResult:
    objective: str
    constraints: list[str]
    proxies: list[str]
    failure_surfaces: list[str]
    invariant_check: str
    invariant_note: str
    minimal_repair: str
    final_judgment: str
    confidence: str


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_units(text: str) -> list[str]:
    chunks = re.split(r"(?<=[\.\?\!])\s+|\n+", text)
    return [_normalize_whitespace(chunk) for chunk in chunks if _normalize_whitespace(chunk)]


def _first_matching_unit(units: list[str], cues: tuple[str, ...]) -> str | None:
    lowered = [(unit, unit.lower()) for unit in units]
    for cue in cues:
        for unit, lower in lowered:
            if cue in lower:
                return unit
    return None


def _extract_objective(units: list[str]) -> tuple[str, bool]:
    explicit = _first_matching_unit(units, OBJECTIVE_CUES)
    if explicit:
        return explicit, False

    fallback = units[0] if units else "Objective under-specified."
    return fallback, True


def _extract_constraints(units: list[str], objective: str) -> list[str]:
    constraints: list[str] = []
    for unit in units:
        if unit == objective:
            continue
        lower = unit.lower()
        if any(cue in lower for cue in CONSTRAINT_CUES):
            constraints.append(unit)

    if not constraints:
        constraints.append("No explicit constraints stated.")

    return constraints[:4]


def _extract_proxies(units: list[str], objective: str) -> list[str]:
    proxies: list[str] = []
    for unit in units:
        if unit == objective:
            continue
        lower = unit.lower()
        if any(pattern in lower for pattern in PROXY_PATTERNS) or any(cue in lower for cue in PROXY_SIGNAL_CUES):
            proxies.append(unit)

    if not proxies:
        proxies.append("No explicit proxies stated.")

    return proxies[:4]


def _has_broad_objective(objective: str) -> bool:
    lower = objective.lower()
    return any(pattern in lower for pattern in BROAD_OBJECTIVE_PATTERNS)


def _has_narrow_proxy_signal(proxies: list[str]) -> bool:
    for proxy in proxies:
        lower = proxy.lower()
        if any(cue in lower for cue in PROXY_SIGNAL_CUES) and any(pattern in lower for pattern in NARROW_PROXY_PATTERNS):
            return True
    return False


def _map_failure_surfaces(
    text: str,
    objective: str,
    objective_inferred: bool,
    constraints: list[str],
    proxies: list[str],
) -> list[str]:
    lower = text.lower()
    failures: list[str] = []
    broad_objective = _has_broad_objective(objective)
    narrow_proxy = _has_narrow_proxy_signal(proxies)

    if proxies and proxies[0] != "No explicit proxies stated.":
        failures.append("Proxy Substitution")
        if any(term in lower for term in OPTIMIZATION_CUES):
            failures.append("Optimization Drift")
        if any(term in lower for term in ("game", "gaming", "exploit", "reward", "incentive", "bonus")):
            failures.append("Exploit Surfaces")
    elif broad_objective and any(cue in lower for cue in PROXY_SIGNAL_CUES) and any(
        pattern in lower for pattern in NARROW_PROXY_PATTERNS
    ):
        failures.append("Proxy Substitution")
        failures.append("Optimization Drift")

    if broad_objective and narrow_proxy and "Proxy Substitution" not in failures:
        failures.append("Proxy Substitution")
        failures.append("Optimization Drift")

    if any(item == "No explicit constraints stated." for item in constraints):
        failures.append("Constraint Erosion")

    if objective_inferred:
        failures.append("Objective Ambiguity Collapse")

    if not failures and any(term in lower for term in OPTIMIZATION_CUES):
        failures.append("Optimization Drift")

    ordered = [name for name in FAILURE_PRIORITY if name in failures]
    if not ordered:
        ordered.append("No structural failure surface detected.")
    return ordered


def _invariant_check(
    objective_inferred: bool,
    proxies: list[str],
    failure_surfaces: list[str],
) -> tuple[str, str]:
    if "Proxy Substitution" in failure_surfaces:
        return "FAIL", "Proxy detected as optimization target."
    if objective_inferred:
        return "FAIL", "Original objective is ambiguous and defaults toward proxy selection."
    if "Constraint Erosion" in failure_surfaces and proxies[0] != "No explicit proxies stated.":
        return "FAIL", "Constraints are too weak to resist optimization pressure."
    return "PASS", "Original objective remains primary under stated structure."


def _minimal_repair(
    objective: str,
    constraints: list[str],
    proxies: list[str],
    failure_surfaces: list[str],
) -> str:
    if "Proxy Substitution" in failure_surfaces:
        return "Restate that proxies are monitoring signals only and bind evaluation back to the original objective."
    if "Objective Ambiguity Collapse" in failure_surfaces:
        return f"State the objective explicitly as: {objective}"
    if "Constraint Erosion" in failure_surfaces:
        return "Add one explicit non-negotiable constraint tied to preserving the original objective."
    if "Optimization Drift" in failure_surfaces:
        return "Add a constraint that measurable indicators cannot override the stated objective."
    return "No repair required beyond preserving the current objective and constraints."


def _final_judgment(invariant_check: str, failure_surfaces: list[str]) -> str:
    if invariant_check == "PASS":
        return "Structurally aligned under current optimization pressure."
    if "Proxy Substitution" in failure_surfaces:
        return "Structurally misaligned through proxy drift."
    if "Objective Ambiguity Collapse" in failure_surfaces:
        return "Structurally unstable because the objective is under-specified."
    return "Structurally misaligned under optimization pressure."


def _confidence(objective_inferred: bool, proxies: list[str]) -> str:
    if objective_inferred:
        return "LOW"
    if proxies[0] == "No explicit proxies stated.":
        return "MEDIUM"
    return "HIGH"


def evaluate_cass_v_lite(text: str) -> str:
    normalized = _normalize_whitespace(text)
    units = _split_units(text)

    objective, objective_inferred = _extract_objective(units)
    constraints = _extract_constraints(units, objective)
    proxies = _extract_proxies(units, objective)
    failure_surfaces = _map_failure_surfaces(normalized, objective, objective_inferred, constraints, proxies)
    invariant_check, invariant_note = _invariant_check(objective_inferred, proxies, failure_surfaces)
    minimal_repair = _minimal_repair(objective, constraints, proxies, failure_surfaces)
    final_judgment = _final_judgment(invariant_check, failure_surfaces)
    confidence = _confidence(objective_inferred, proxies)

    result = AuditResult(
        objective=objective,
        constraints=constraints,
        proxies=proxies,
        failure_surfaces=failure_surfaces,
        invariant_check=invariant_check,
        invariant_note=invariant_note,
        minimal_repair=minimal_repair,
        final_judgment=final_judgment,
        confidence=confidence,
    )
    return format_cass_v_lite(result)


def format_cass_v_lite(result: AuditResult) -> str:
    lines = [
        "Objective:",
        result.objective,
        "",
        "Constraints:",
    ]
    lines.extend(f"- {item}" for item in result.constraints)
    lines.extend(
        [
            "",
            "Proxies:",
        ]
    )
    lines.extend(f"- {item}" for item in result.proxies)
    lines.extend(
        [
            "",
            "Failure Surfaces:",
        ]
    )
    lines.extend(f"- {item}" for item in result.failure_surfaces)
    lines.extend(
        [
            "",
            "Invariant Check:",
            result.invariant_check,
            result.invariant_note,
            "",
            "Minimal Repair:",
            result.minimal_repair,
            "",
            "Final Judgment:",
            result.final_judgment,
            "",
            "Confidence:",
            result.confidence,
        ]
    )
    return "\n".join(lines)


def main() -> int:
    text = sys.stdin.read()
    if not text.strip() and len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    if not text.strip():
        return 1
    sys.stdout.write(evaluate_cass_v_lite(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
