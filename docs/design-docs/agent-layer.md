# Agent Layer Design — dua multi-agent LLM vao harness (proposal-only)

## Trang thai: slice 1 DONE (2026-09-13) — pipeline + provider seam, offline 100%.
Con lai: provider that/secrets/tokens/LangGraph/live-fire (can human, decision 0001).

## Nguon
Kien truc 4-agent cua QuantHarness (Y-Research-SBU, MIT, arXiv 2509.09995):
Indicator → Pattern → Trend → Decision (LangGraph, vision charts, yfinance).
Noi dung duoi day viet lai hoan toan cho harness nay — khong copy code.

## Nguyen tac tich hop (bat buoc)
1. **Agents propose, gate disposes.** LLM chi duoc de xuat (hypothesis, regime read,
   candidate params). Thang/qu thua do `evals/gate.py` quyet. Khong verdict nao tu
   LLM duoc promote ma chua qua gate.
2. **Tools deterministic, LLM thay the duoc.** Indicator (RSI/MACD/Stoch) tinh bang
   pandas seeded — khong phai loi LLM. LLM nam sau `Providers.llm` protocol de mock
   trong test (deterministic replay). Pattern/trend vision la optional, output phai
   validate Pydantic truoc khi vao decision.
3. **Khong cam HOLD, khong ep LONG/SHORT.** Quyet dinh cuoi la position sizing +
   kill-criteria trong risk service, khong phai enum cung tu prompt.
4. **No lookahead ke ca voi LLM.** Context dua cho LLM chi chua bars `ts <= t`
   + universe members tai t. Prompt chua du lieu tuong lai = P0 nhu code.
5. **Chi phi + nondeterminism phai thay duoc.** Moi LLM call ghi vao traces.jsonl
   (model, tokens, seed). Eval khong bao gio phu thuoc output LLM truc tiep —
   chi phu thuoc params/config LLM de xuat.

## Map vao layers hien co
- `src/domains/alpha/tools.py` (moi): indicator thuan, pandas-only (khong TA-Lib de giu boring deps).
- `src/domains/alpha/schemas.py` (moi): `IndicatorReport`, `PatternReport`, `TrendReport`, `Proposal` (Pydantic).
- `src/providers/llm.py` (moi): `LLMProvider` protocol + `ReplayLLM` (test) + `LiveLLM` (API, secrets qua env).
- `src/domains/alpha/agents.py` (moi): orchestration 4 buoc thuan tuy (khong LangGraph luc dau —
  them khi can branch/loop phuc tap; YAGNI).
- Gate giu nguyen lam promotion authority; K trials bao gom so proposal LLM da thu.

## Khong lay tu QuantHarness
Flask UI (harness khong UI), API-key-qua-UI, forced LONG/SHORT, TA-Lib, langchain deps nang
(tru khi agent-layer can that — Chung minh bang exec-plan truoc).

## Dieu kien implement (tech-debt)
Can quyet dinh provider + secrets policy + ngan sach tokens truoc khi code (decision 0001:
day la material choice — dung va hoi human).
