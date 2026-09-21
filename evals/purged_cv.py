"""Purged-embargo K-fold splits for time series.

The test fold is contiguous. Training removes purge bars around the test fold
and embargo bars after it.
"""
from __future__ import annotations


def purged_embargo_splits(n: int, n_folds: int = 3, purge: int = 21, embargo: int = 5):
    assert n_folds >= 2, "need >=2 folds"
    assert n > n_folds * (purge + embargo + 1), "not enough bars for folds+purge+embargo"
    fold = n // n_folds
    out = []
    for k in range(n_folds):
        a = k * fold
        b = n if k == n_folds - 1 else (k + 1) * fold
        train = [i for i in range(n) if i < a - purge or i > b + embargo]
        out.append((train, list(range(a, b))))
    return out
