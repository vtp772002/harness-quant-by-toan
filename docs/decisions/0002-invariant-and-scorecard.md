# 0002 — Every Rule Needs a Guard and Behavioral Scorecard

- Date: 2026-09-13. Status: accepted.
- Inspired by harness-by-victoria (`encode-invariant` and harness evaluation).

## Context
The repository has many standards (`NO_LOOKAHEAD`, `REPRODUCIBILITY`, and
`RISK_LIMITS`), but only linters and tests turn them into enforceable rules. A
common contract is needed for every new rule.

## Decision
1. A new rule is accepted only with an executable guard (a linter or test owned
   by the existing framework), positive and negative proof, and a diagnostic
   that identifies the violation and fix. See
   `.agents/skills/encode-invariant/`.
2. `scripts/evaluate-quant-harness.py` is the harness health measure. It emits
   versioned JSON (`quant-scorecard-v1`) for local and CI use. A blocking case
   failure prevents merge.
3. Do not infer policy from old conventions or code. An old check without
   authority is a mismatch to report, not a basis for expansion.

## Consequences
- Adding a rule means adding a guard and proof, not another paragraph.
- The scorecard replaces the feeling that the harness is healthy with evidence.
