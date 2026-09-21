"""Deflated Sharpe Ratio (Bailey and Lopez de Prado, 2014).

The Phi and inverse-Phi functions use `erf` and Acklam to keep dependencies
boring and deterministic. All values use the observation frequency (daily):
`sr_hat` is daily Sharpe and `t` is the number of returns.
"""
from __future__ import annotations

import math


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def phi_inv(p: float) -> float:
    assert 0.0 < p < 1.0, "p must be in (0,1)"
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def expected_sharpe_null(trial_var: float, n_trials: int) -> float:
    if n_trials < 2 or trial_var <= 0:
        return 0.0
    g = 0.5772156649
    return math.sqrt(trial_var) * ((1 - g) * phi_inv(1 - 1 / n_trials) + g * phi_inv(1 - 1 / (n_trials * math.e)))


def return_moments(rets) -> tuple[float, float, float]:
    import numpy as np
    r = np.asarray(list(rets), dtype=float)
    s = r.std()
    if s == 0 or len(r) < 3:
        return (0.0, 0.0, 3.0)
    z = (r - r.mean()) / s
    return (float(r.mean() / s), float((z ** 3).mean()), float((z ** 4).mean()))


def deflated_sharpe(sr_hat: float, t: int, skew: float, kurt: float, trial_var: float, n_trials: int) -> float:
    sr0 = expected_sharpe_null(trial_var, n_trials)
    den = math.sqrt(max(1e-12, 1 - skew * sr_hat + (kurt - 1) / 4 * sr_hat ** 2))
    return phi((sr_hat - sr0) * math.sqrt(max(t - 1, 1)) / den)
