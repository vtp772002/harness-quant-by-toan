# Agent Layer Design — Multi-Agent LLM Proposal Layer

## Status: slice 1 complete (2026-09-13)

The deterministic pipeline and provider seam are complete and fully offline.
Real providers, secrets, token budgets, LangGraph, and live-fire validation
remain deferred pending human decisions under decision `0001`.

## Source

The conceptual four-agent architecture is inspired by QuantHarness
(Y-Research-SBU, MIT, arXiv 2509.09995): Indicator → Pattern → Trend →
Decision, with LangGraph, chart vision, and yfinance in that project. The design
below is rewritten for this harness and does not copy its code.

## Integration principles (mandatory)

1. **Agents propose, gate disposes.** The LLM may propose a hypothesis, regime
   read, or candidate parameters. `evals/gate.py` decides success or failure.
   No LLM verdict is promoted without passing the gate.
2. **Tools are deterministic and the LLM is replaceable.** RSI, MACD, and Stoch
   use seeded pandas calculations; they are not LLM work. The LLM sits behind
   `Providers.llm` so tests can use deterministic replay. Optional pattern or
   trend vision must be validated by Pydantic before a decision.
3. **Do not force HOLD, LONG, or SHORT.** The final decision is position sizing
   plus risk-service kill criteria, not an enum copied from a prompt.
4. **No lookahead, including for LLM context.** LLM context contains only bars
   with `ts <= t` and universe members at `t`. Future data in a prompt is a P0
   violation, just like future data in code.
5. **Cost and nondeterminism must be visible.** Every LLM call records model,
   tokens, and seed in `traces.jsonl`. Evaluation must never depend directly on
   raw LLM output; it may depend only on the proposed parameters/configuration.

## Mapping to existing layers

- `src/domains/alpha/tools.py`: pure pandas-only indicators; no TA-Lib so the
  dependency surface stays boring.
- `src/domains/alpha/schemas.py`: `IndicatorReport`, `PatternReport`,
  `TrendReport`, `Proposal`, and Pydantic validation.
- `src/providers/llm.py`: `LLMProvider`, `ReplayLLM` for tests, and `LiveLLM`
  with secrets supplied through the environment.
- `src/domains/alpha/agents.py`: a four-step orchestration pipeline. LangGraph
  is deferred until branching or looping complexity justifies it.
- The gate remains the promotion authority; `K` includes the LLM proposals tried.

## Explicitly excluded

Do not add a Flask UI, API-key-through-UI flow, forced LONG/SHORT behavior,
TA-Lib, or heavy LangChain dependencies unless an execution plan proves the
agent layer needs them.

## Implementation gate

Provider choice, secrets policy, and token budget must be decided before new
production code is written. This is a material choice under decision `0001`:
stop and ask the human rather than inventing policy.
