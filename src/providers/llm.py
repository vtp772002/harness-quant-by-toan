"""LLM provider protocol — LLM nam sau interface nay de mock trong test.
ReplayLLM: deterministic replay cho test/CI (khong goi mang).
LiveLLM: OpenAI-compatible HTTPS bang stdlib; chi chay khi co key (khong bao gio trong CI).
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from typing import Protocol
from src.domains.alpha.schemas import Proposal, ProposalContext


class LLMError(Exception):
    pass


class LLMProvider(Protocol):
    @property
    def model_id(self) -> str: ...
    def propose(self, ctx: ProposalContext) -> Proposal: ...


class ReplayLLM:
    """Chon canned response bang hash cua context — stateless, deterministic, khong mang."""

    def __init__(self, canned: list[dict], model_id: str = "replay-v1"):
        if not canned:
            raise LLMError("ReplayLLM can it nhat 1 canned response")
        self._canned = canned
        self._id = model_id

    @property
    def model_id(self) -> str:
        return self._id

    def propose(self, ctx: ProposalContext) -> Proposal:
        h = hashlib.sha256(ctx.model_dump_json().encode()).hexdigest()
        d = dict(self._canned[int(h, 16) % len(self._canned)])
        d.setdefault("model", self._id)
        d["symbol"], d["ts"], d["asof"] = ctx.symbol, ctx.ts, ctx.asof
        return Proposal.model_validate(d)


class LiveLLM:
    """OpenAI-compatible chat endpoint. Secrets qua env, khong hardcode."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None,
                 base_url: str = "https://api.openai.com/v1", timeout: int = 60):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise LLMError("Thieu OPENAI_API_KEY (env hoac truyen vao). Khong goi LiveLLM trong test/CI.")
        self._model, self._key, self._base, self._timeout = model, key, base_url.rstrip("/"), timeout

    @property
    def model_id(self) -> str:
        return self._model

    def propose(self, ctx: ProposalContext) -> Proposal:
        body = {"model": self._model, "temperature": 0.1, "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "Ban la quant research assistant. Tra ve DUY NHAT JSON khop Proposal: direction (long/short/flat), confidence 0..1, candidate_lookbacks (ints), rationale ngan."},
                    {"role": "user", "content": ctx.model_dump_json()}]}
        req = urllib.request.Request(self._base + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": "Bearer " + self._key,
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                payload = json.loads(resp.read().decode())
            content = payload["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            d = json.loads(content)
        except LLMError:
            raise
        except Exception as e:  # noqa: BLE001 — bien moi loi transport/parse thanh LLMError
            raise LLMError(f"LLM call that bai: {e}")
        d["symbol"], d["ts"], d["asof"] = ctx.symbol, ctx.ts.isoformat(), ctx.asof.isoformat()
        d.setdefault("model", self._model)
        try:
            return Proposal.model_validate(d)
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"LLM tra ve Proposal khong hop le: {e}")
