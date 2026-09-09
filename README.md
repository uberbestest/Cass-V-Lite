# Cass-V Lite

**AI evaluation · agent safety · objective drift · specification gaming · proxy substitution · governance evaluation · structural alignment**

[Support Josh Young's independent evaluation research](https://cash.app/$uberbestest1)

Cass-V Lite is a small structural audit tool for checking whether a stated objective survives optimization pressure.

It is meant for quick, grounded evaluation of systems, plans, prompts, and governance designs. The tool looks for cases where a proxy, metric, reward signal, or vague target can replace the original objective.

It does not evaluate ethics, quality, persuasiveness, or policy merit. It checks structural alignment only.

## What It Reports

Cass-V Lite returns a fixed text report with these sections:

- `Objective`
- `Constraints`
- `Proxies`
- `Failure Surfaces`
- `Invariant Check`
- `Minimal Repair`
- `Final Judgment`
- `Confidence`

The output structure is part of the project contract and is covered by tests.

## Run

Pass text as an argument:

```powershell
python cass_v_lite.py "Objective: Improve student learning outcomes. Measure success by average test score."
```

Or pipe text through standard input:

```powershell
"Objective: Keep support accurate. Optimize for ticket throughput." | python cass_v_lite.py
```

## Examples

Example inputs and outputs are in `examples/`:

- `examples/aligned_system_input.txt`
- `examples/aligned_system_output.txt`
- `examples/proxy_drift_input.txt`
- `examples/proxy_drift_output.txt`
- `examples/ambiguous_objective_input.txt`
- `examples/ambiguous_objective_output.txt`

These are plain text snapshots for first-time readers and for manual comparison. The automated tests remain in `test_cass_v_lite.py`.

## Tests

```powershell
python -m unittest
```

The tests cover aligned systems, proxy-heavy systems, ambiguous objectives, over-optimized systems, and the exact ordering of output sections.

## Files

- `cass_v_lite.py` contains the audit logic and command-line entry point.
- `test_cass_v_lite.py` contains the unit tests.
- `examples/` contains small input/output samples.

## Scope

Cass-V Lite is intentionally narrow. It does not include multi-agent reasoning, recursive refinement, adversarial testing, or broader framework expansion.

Use it as a first structural pass: identify the objective, locate constraints, surface proxy pressure, and return the smallest repair that keeps the original objective primary.

## Status

Local working prototype with unit tests.
