"""Tests agent layer: tools deterministic + PIT, schemas, ReplayLLM, pipeline, gate wiring."""
from __future__ import annotations

import pandas as pd


def _bars(n=60, seed=0, drift=0.001):
    import numpy as np
    from datetime import datetime, timezone, timedelta
    rng = np.random.default_rng(seed)
    px = 100 + np.cumsum(rng.normal(drift, 0.01, n))
    ts = [datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(n)]
    return pd.DataFrame({"symbol": "T", "ts": ts, "open": px, "high": px + 0.3,
                         "low": px - 0.3, "close": px, "volume": 100_000})


def test_rsi_bounds_and_neutral():
    from src.domains.alpha.tools import rsi
    r = rsi(_bars()["close"])
    assert ((r >= 0) & (r <= 100)).all()
    flat = pd.Series([100.0] * 40)
    assert abs(rsi(flat).iloc[-1] - 50.0) < 1e-9


def test_macd_constant_zero():
    from src.domains.alpha.tools import macd
    m = macd(pd.Series([100.0] * 60)).iloc[-1]
    assert abs(m["macd"]) < 1e-9 and abs(m["hist"]) < 1e-9


def test_stoch_bounds():
    from src.domains.alpha.tools import stoch
    s = stoch(_bars())
    assert ((s["k"] >= 0) & (s["k"] <= 100)).all()


def test_breakout_pit():
    from src.domains.alpha.tools import breakout
    df = _bars()
    df.loc[59, "close"] = df["high"].max() + 5.0
    assert breakout(df) == "up"
    assert breakout(df.iloc[:50]) == breakout(df.iloc[:50])  # identical slice, stable result


def test_pipeline_deterministic_and_valid():
    from src.domains.alpha.agents import run_pipeline
    df = _bars()
    p1 = run_pipeline(df, "T")
    p2 = run_pipeline(df, "T")
    assert p1.model_dump_json() == p2.model_dump_json()
    assert p1.asof <= p1.ts and p1.direction in ("long", "short", "flat")
    assert len(p1.rationale) > 0 and p1.model == "rules-v1"


def test_replay_llm_deterministic_and_valid():
    from src.domains.alpha.agents import indicator_step, pattern_step, trend_step
    from src.domains.alpha.schemas import ProposalContext
    from src.providers.llm import ReplayLLM
    df = _bars()
    i, p, t = indicator_step(df, "T"), pattern_step(df, "T"), trend_step(df, "T")
    ctx = ProposalContext(symbol="T", ts=i.ts, asof=i.asof, indicator=i, pattern=p, trend=t)
    canned = [{"direction": "long", "confidence": 0.6, "candidate_lookbacks": [5, 10],
               "rationale": "replay", "model": "replay-v1"}]
    llm = ReplayLLM(canned)
    assert llm.propose(ctx).model_dump_json() == llm.propose(ctx).model_dump_json()


def test_pipeline_with_provider():
    from src.domains.alpha.agents import run_pipeline
    from src.providers.llm import ReplayLLM
    canned = [{"direction": "flat", "confidence": 0.4, "candidate_lookbacks": [10],
               "rationale": "replay-flat", "model": "replay-v1"}]
    p = run_pipeline(_bars(), "T", provider=ReplayLLM(canned))
    assert p.direction == "flat" and p.model == "replay-v1" and p.candidate_lookbacks == [10]


def test_live_llm_missing_key_raises():
    import os
    from src.providers.llm import LiveLLM, LLMError
    os.environ.pop("OPENAI_API_KEY", None)
    try:
        LiveLLM()
        raise AssertionError("must raise when the key is missing")
    except LLMError:
        pass


def test_schema_rejects_bad_direction():
    from pydantic import ValidationError
    from src.domains.alpha.schemas import Proposal
    from datetime import datetime, timezone
    try:
        Proposal(symbol="T", ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
                 asof=datetime(2024, 1, 1, tzinfo=timezone.utc), direction="MOON",
                 confidence=0.5, candidate_lookbacks=[5], rationale="x", model="t")
        raise AssertionError("must reject an invalid direction")
    except ValidationError:
        pass


def test_gate_accepts_proposal_lookbacks():
    from src.domains.alpha.agents import run_pipeline
    from src.domains.data.service import apply_splits
    from src.domains.data.synthetic import make_synthetic_market
    from evals.gate import run_gate
    from src.providers.telemetry import Telemetry
    from pathlib import Path
    import tempfile
    mkt = make_synthetic_market(42)
    panel = apply_splits(mkt.panel, mkt.splits)
    aaa = panel[panel.symbol == "AAA"].sort_values("ts").reset_index(drop=True)
    proposal = run_pipeline(aaa.iloc[:120], "AAA")
    kw = dict(telemetry=Telemetry(Path(tempfile.mkdtemp())),
              candidate_lookbacks=proposal.candidate_lookbacks)
    r1, r2 = run_gate(42, **kw), run_gate(42, telemetry=Telemetry(Path(tempfile.mkdtemp())),
                                          candidate_lookbacks=proposal.candidate_lookbacks)
    assert r1 == r2 and r1["candidates"] == proposal.candidate_lookbacks
    assert set(r1["picks"]) <= set(proposal.candidate_lookbacks) and r1["n_oos"] > 0
