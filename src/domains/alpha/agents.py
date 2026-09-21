"""Deterministic four-step agent pipeline: indicator, pattern, trend, decision.

Rules-v1 is the fallback and numeric source of truth. An LLM may add narrative,
but its proposal still goes through schema validation and the same gate.
"""
from __future__ import annotations
import pandas as pd
from src.domains.alpha import tools
from src.domains.alpha.schemas import (
    IndicatorReport, IndicatorValues, PatternReport, Proposal, ProposalContext, TrendReport)
from src.providers.llm import LLMProvider

BASE_LOOKBACKS = [5, 10, 20]


def _last(s: pd.Series, default: float) -> float:
    v = s.iloc[-1]
    return default if pd.isna(v) else float(v)


def indicator_step(bars_asof: pd.DataFrame, symbol: str) -> IndicatorReport:
    c = bars_asof["close"]
    m = tools.macd(c).iloc[-1]
    s = tools.stoch(bars_asof).iloc[-1]
    last = bars_asof.iloc[-1]
    vals = IndicatorValues(
        rsi=_last(tools.rsi(c), 50.0),
        macd=0.0 if pd.isna(m["macd"]) else float(m["macd"]),
        macd_signal=0.0 if pd.isna(m["signal"]) else float(m["signal"]),
        macd_hist=0.0 if pd.isna(m["hist"]) else float(m["hist"]),
        stoch_k=float(s["k"]), stoch_d=float(s["d"]),
        roc=_last(tools.roc(c), 0.0),
        willr=_last(tools.willr(bars_asof), -50.0),
        atr=_last(tools.atr(bars_asof), float(last["close"]) * 0.01),
    )
    return IndicatorReport(symbol=symbol, ts=last["ts"], asof=last["ts"], values=vals)


def pattern_step(bars_asof: pd.DataFrame, symbol: str, window: int = 20) -> PatternReport:
    last = bars_asof.iloc[-1]
    return PatternReport(symbol=symbol, ts=last["ts"], asof=last["ts"],
                         breakout=tools.breakout(bars_asof, window),
                         engulfing=tools.engulfing(bars_asof),
                         range_position=tools.range_position(bars_asof, window))


def trend_step(bars_asof: pd.DataFrame, symbol: str, window: int = 30) -> TrendReport:
    slope, r2 = tools.trend_slope(bars_asof, window)
    last = bars_asof.iloc[-1]
    if slope > 5 and r2 > 0.3:
        regime = "up"
    elif slope < -5 and r2 > 0.3:
        regime = "down"
    else:
        regime = "range"
    return TrendReport(symbol=symbol, ts=last["ts"], asof=last["ts"], slope_bps=slope,
                       r_squared=r2, channel_position=tools.range_position(bars_asof, window),
                       regime=regime)


def _rules_proposal(symbol: str, bars_asof: pd.DataFrame, i: IndicatorReport,
                    p: PatternReport, t: TrendReport) -> Proposal:
    votes = [1.0 if i.values.rsi > 50 else -1.0,
             1.0 if i.values.macd_hist > 0 else -1.0,
             1.0 if t.slope_bps > 0 else -1.0,
             1.0 if p.breakout == "up" else (-1.0 if p.breakout == "down" else 0.0),
             1.0 if p.engulfing == "bull" else (-1.0 if p.engulfing == "bear" else 0.0)]
    score = sum(votes) / len(votes)
    direction = "long" if score > 0.2 else ("short" if score < -0.2 else "flat")
    last = bars_asof.iloc[-1]
    rationale = (f"votes={score:.2f} rsi={i.values.rsi:.1f} macd_hist={i.values.macd_hist:.4f} "
                 f"slope={t.slope_bps:.1f}bps r2={t.r_squared:.2f} breakout={p.breakout} "
                 f"engulf={p.engulfing} regime={t.regime}")
    return Proposal(symbol=symbol, ts=last["ts"], asof=last["ts"], direction=direction,
                    confidence=abs(score), candidate_lookbacks=list(BASE_LOOKBACKS),
                    rationale=rationale, model="rules-v1")


def run_pipeline(bars_asof: pd.DataFrame, symbol: str,
                 provider: LLMProvider | None = None) -> Proposal:
    """Run four steps; use a validated LLM proposal or the rules-v1 fallback."""
    i = indicator_step(bars_asof, symbol)
    p = pattern_step(bars_asof, symbol)
    t = trend_step(bars_asof, symbol)
    if provider is None:
        return _rules_proposal(symbol, bars_asof, i, p, t)
    ctx = ProposalContext(symbol=symbol, ts=i.ts, asof=i.asof,
                          indicator=i, pattern=p, trend=t)
    proposal = provider.propose(ctx)
    assert proposal.asof <= proposal.ts, "LLM proposal violates asof<=ts"
    return proposal
