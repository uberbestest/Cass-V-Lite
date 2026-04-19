# Cass-V Lite

A minimal executable version of the Cass-V structural audit framework.

A single-pass structural audit tool for evaluating whether a system remains aligned with its original objective under optimization pressure.

Cass-V Lite identifies:

- the true objective  
- constraints  
- proxies / reward signals  
- failure surfaces  

It returns a strict structural judgment.

This tool does not evaluate ethics, quality, or persuasiveness.  
It evaluates structural integrity only.

## Example

Input:  
Improve student learning outcomes. Measure success by average test score.

Output:  
FAIL — proxy substitution (test score used as optimization target)

---

## Why it exists

Many systems drift because they optimize proxies instead of their original objective.

Cass-V Lite is designed to detect:

- proxy substitution  
- optimization drift  
- constraint erosion  

before those failures become embedded.

---

## How to run

Run:

python cass_v_lite.py "Objective: Improve student learning outcomes. Measure success by average test score."

or

echo "Objective: Keep support accurate. Optimize for ticket throughput." | python cass_v_lite.py

---

## Example Output

Objective:
Improve student learning outcomes.

Constraints:
- No explicit constraints stated.

Proxies:
- Measure success by average test score.

Failure Surfaces:
- Proxy Substitution
- Optimization Drift
- Constraint Erosion

Invariant Check:
FAIL

Final Judgment:
Structurally misaligned through proxy drift.

---

## Scope (Important)

Cass-V Lite is intentionally minimal.

It does not include:

- multi-agent reasoning  
- recursive refinement  
- adversarial mirror testing  
- deep constraint reconstruction  

Those exist in the full system.

---

## Status

Initial release candidate

Validated on multiple proxy-substitution test cases
