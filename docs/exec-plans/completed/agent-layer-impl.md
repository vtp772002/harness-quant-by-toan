# Exec Plan: Agent-Layer Slice 1 (Deterministic Pipeline and LLM Seam)

## Goal

Agents propose hypotheses and parameters; the gate decides the verdict. Slice 1
is fully offline and deterministic.

## Scope (complete)

- `alpha/tools.py`: RSI, MACD, Stoch, ROC, WillR, ATR, breakout, engulfing,
  range, and trend-slope tools using pandas and point-in-time inputs.
- `alpha/schemas.py`: Indicator, Pattern, TrendReport, Proposal, and
  ProposalContext schemas using Pydantic.
- `providers/llm.py`: `LLMProvider`, `ReplayLLM` for tests, and `LiveLLM` with
  an optional key and standard-library HTTPS.
- `alpha/agents.py`: four-step pipeline, rules-v1 fallback, provider path,
  validation, and `asof <= ts` assertion.
- `evals/gate.py`: accepts `candidate_lookbacks` from Proposal and sets
  `K = len(candidates)`.

## Not included (deferred; requires a human decision)

Real provider selection, secrets policy, token budget, LangGraph, and live-fire
validation remain governed by decision `0001`.

## Acceptance

Linters pass, the ten agent-layer tests pass, seed-42 gate output is
byte-identical across repeated runs, and the scorecard passes. The plan is
complete and belongs in `completed/`.
