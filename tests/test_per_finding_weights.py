"""Tests for the off-gold per-finding blend weights (E106).

Six schemes in `EXPERIMENTS.md` were refused for choosing a blend weight on the
58 expert studies and reporting the result on those same 58. This one is only
different because of where the weight comes from — fitted on 4,349 non-gold
studies, tested on the 58 the fit never saw. **That split is the entire claim**,
so it is asserted here rather than trusted to stay true through future edits.

The other failure modes these cover:

1. **A free parameter sneaking in.** The formula is skill above chance,
   normalised. A threshold, a floor or a shrinkage term would each be a number
   chosen by someone who had seen the answer, and each would look harmless.
2. **A nan reaching a submission.** A finding with one class on the fit set has
   an undefined AUC; unguarded, its weight is nan and that column's ordering is
   destroyed while the file still looks valid.
3. **The degenerate tie.** If neither arm beats chance the denominator is zero.
   No information means no opinion, which is 0.5, not a crash and not 0.

No patient data: every array here is written for the test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "eda"))

import per_finding_weights as pfw  # noqa: E402


def _truth(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(n, len(pfw.FINDINGS))).astype(float)


# --------------------------------------------------------------------------- #
# The split, which is the whole claim
# --------------------------------------------------------------------------- #
def test_a_gold_study_reaching_the_fit_is_refused_not_warned_about():
    """THE GUARD THIS FILE EXISTS FOR. A silent leak here makes the held-out
    number circular while it still prints and still looks like a validation."""
    t = _truth()
    mask = np.zeros(len(t), bool)
    mask[7] = True
    with pytest.raises(ValueError, match="gold studies reached the weight fit"):
        pfw.fit_weights(t, np.random.rand(*t.shape), np.random.rand(*t.shape),
                        gold_mask=mask)


def test_the_fit_runs_when_no_gold_is_present():
    t = _truth()
    w, table = pfw.fit_weights(t, np.random.rand(*t.shape), np.random.rand(*t.shape),
                               gold_mask=np.zeros(len(t), bool))
    assert w.shape == (len(pfw.FINDINGS),)
    assert list(table.finding) == pfw.FINDINGS


# --------------------------------------------------------------------------- #
# The formula
# --------------------------------------------------------------------------- #
def test_an_arm_that_is_perfect_where_the_other_is_chance_takes_all_the_weight():
    """The MCL case in miniature: CoAtNet 0.982 against v1 0.882 is what the
    uniform 0.5 weight was destroying (E105, −0.032 on that finding alone)."""
    n = 200
    t = np.tile(np.repeat([0.0, 1.0], n // 2)[:, None], (1, len(pfw.FINDINGS)))
    perfect = np.tile(np.arange(n, dtype=float)[:, None], (1, len(pfw.FINDINGS)))
    chance = np.zeros_like(perfect)
    w, _ = pfw.fit_weights(t, coat=perfect, v1=chance)
    assert np.allclose(w, 0.0), "the chance arm still got weight"
    w2, _ = pfw.fit_weights(t, coat=chance, v1=perfect)
    assert np.allclose(w2, 1.0), "the perfect arm did not take the weight"


def test_two_equally_skilled_arms_split_the_weight_evenly():
    n = 200
    t = np.tile(np.repeat([0.0, 1.0], n // 2)[:, None], (1, len(pfw.FINDINGS)))
    same = np.tile(np.arange(n, dtype=float)[:, None], (1, len(pfw.FINDINGS)))
    w, _ = pfw.fit_weights(t, coat=same, v1=same.copy())
    assert np.allclose(w, 0.5)


def test_neither_arm_beating_chance_yields_no_opinion_rather_than_zero():
    """Denominator zero. No information is 0.5, not 0 — a 0 would silently hand
    the finding to whichever arm happened to be first in the signature."""
    n = 40
    t = np.tile(np.repeat([0.0, 1.0], n // 2)[:, None], (1, len(pfw.FINDINGS)))
    # exactly reversed ordering: AUC 0 for both, so skill above chance is 0
    worse = np.tile(np.arange(n, 0, -1, dtype=float)[:, None], (1, len(pfw.FINDINGS)))
    w, _ = pfw.fit_weights(t, coat=worse, v1=worse.copy())
    assert np.allclose(w, 0.5)


def test_the_formula_carries_no_threshold_floor_or_shrinkage_term():
    """Read on the source. Each of those is a number chosen by someone who has
    seen the answer, and each would look like a reasonable safeguard."""
    src = (REPO_ROOT / "eda" / "per_finding_weights.py").read_text()
    body = src[src.index("def fit_weights("):src.index("def blend(")]
    code = "\n".join(line.split("#", 1)[0] for line in body.splitlines())
    literals = {t for t in ("0.9", "0.8", "0.7", "0.6", "0.3", "0.2", "0.1", "0.05")
                if t in code}
    assert not literals, f"fit_weights carries tuned-looking constants {literals}"
    assert "clip" not in code and "minimum" not in code and "maximum" not in code


# --------------------------------------------------------------------------- #
# The blend
# --------------------------------------------------------------------------- #
def test_a_scalar_weight_reproduces_the_uniform_blend():
    """The control has to be the same code path as the treatment, or the
    comparison is between two implementations rather than two weightings."""
    rng = np.random.default_rng(3)
    a, b = rng.random((50, 12)), rng.random((50, 12))
    per_finding = pfw.blend(a, b, np.full(12, 0.5))
    scalar = pfw.blend(a, b, 0.5)
    assert np.allclose(per_finding, scalar)


def test_weight_zero_and_one_return_the_members_themselves():
    rng = np.random.default_rng(4)
    a, b = rng.random((50, 12)), rng.random((50, 12))
    assert np.allclose(pfw.blend(a, b, 0.0), pfw.rankpct(a))
    assert np.allclose(pfw.blend(a, b, 1.0), pfw.rankpct(b))


def test_a_per_finding_weight_touches_only_its_own_column():
    """One column's weight leaking into another is how a per-finding scheme
    silently becomes a worse uniform one."""
    rng = np.random.default_rng(9)
    a, b = rng.random((60, 12)), rng.random((60, 12))
    w = np.full(12, 0.5)
    w[3] = 0.0
    out = pfw.blend(a, b, w)
    ref = pfw.blend(a, b, 0.5)
    assert np.allclose(out[:, 3], pfw.rankpct(a)[:, 3])
    assert np.allclose(np.delete(out, 3, axis=1), np.delete(ref, 3, axis=1))


def test_auc_matches_sklearn_including_ties():
    sk = pytest.importorskip("sklearn.metrics")
    rng = np.random.default_rng(0)
    for _ in range(100):
        n = int(rng.integers(10, 80))
        y = rng.integers(0, 2, n).astype(float)
        if y.min() == y.max():
            continue
        p = np.round(rng.random(n), int(rng.choice([0, 1, 3])))
        assert pfw.auc(y, p) == pytest.approx(sk.roc_auc_score(y, p))


def test_the_coatnet_column_uses_upstreams_published_weights_unchanged():
    """0.55 / 0.20 / 0.15 / 0.10 are the 0.937 write-up's, and they are the one
    set of weights in this pipeline that was never fitted here."""
    assert pfw.PUBLISHED_ARM_WEIGHTS == {
        "maxspan-v5": 0.55, "native384-v8": 0.20,
        "maxspan-v5-reverse": 0.15, "native384dense-v10": 0.10}
    assert sum(pfw.PUBLISHED_ARM_WEIGHTS.values()) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# End to end
# --------------------------------------------------------------------------- #
def test_the_whole_pipeline_recovers_a_planted_per_finding_structure(tmp_path, capsys):
    """A corpus built so that ONE finding wants each extreme.

    MCL is the real case (E105: CoAtNet 0.982, v1 0.882, uniform blending costs
    0.032), so it is planted here as CoAtNet-perfect / v1-at-chance. Baker's is
    planted the other way round, because a rule that only ever pushes weight in
    one direction would pass a one-sided test and still be wrong.

    This runs the actual CLI over an actual parquet and actual fold dumps — the
    unit tests above cover the arithmetic, and this covers the joins, the arbiter
    threshold and the gold/fit split that the arithmetic sits inside.
    """
    import json

    import pandas as pd

    rng = np.random.default_rng(0)
    n, lab = 600, pfw.FINDINGS
    ids = [f"study{i:04d}" for i in range(n)]
    y = rng.integers(0, 2, (n, 12)).astype(float)
    coat = y * 0.55 + rng.random((n, 12)) * 0.45
    v1 = y * 0.45 + rng.random((n, 12)) * 0.55
    mcl, baker = lab.index("MCL"), lab.index("Baker's")
    coat[:, mcl] = y[:, mcl] * 0.95 + rng.random(n) * 0.05
    v1[:, mcl] = rng.random(n)
    v1[:, baker] = y[:, baker] * 0.95 + rng.random(n) * 0.05
    coat[:, baker] = rng.random(n)

    blocks = []
    for arm in pfw.PUBLISHED_ARM_WEIGHTS:
        d = pd.DataFrame(coat + rng.normal(0, 0.02, coat.shape), columns=lab)
        d.insert(0, "arm", arm)
        d.insert(0, "StudyInstanceUID", ids)
        blocks.append(d)
    pd.concat(blocks, ignore_index=True).to_parquet(tmp_path / "coat.parquet", index=False)
    for fold in range(5):
        chunk = slice(fold * 120, (fold + 1) * 120)
        (tmp_path / f"oof_all_fold{fold}.json").write_text(json.dumps(
            {"fold": fold, "findings": lab, "studies": ids[chunk],
             "predicted": v1[chunk].tolist()}))
    labels = pd.DataFrame(y, columns=lab)
    labels.insert(0, "StudyInstanceUID", ids)
    labels.to_csv(tmp_path / "labels.csv", index=False)
    train = pd.DataFrame({"StudyInstanceUID": ids})
    for k, finding in enumerate(lab):
        train[finding] = [y[i, k] if i < 58 else np.nan for i in range(n)]
    train.to_csv(tmp_path / "train.csv", index=False)

    assert pfw.main(["--coat", str(tmp_path / "coat.parquet"),
                     "--v1", str(tmp_path / "oof_all_fold*.json"),
                     "--labels", str(tmp_path / "labels.csv"),
                     "--gold", str(tmp_path / "train.csv")]) == 0
    out = capsys.readouterr().out
    assert "gold studies (TEST set, never fitted on): 58" in out
    assert "fit studies (non-gold, report-labelled): 542" in out

    row = {line.split()[0]: line for line in out.splitlines() if line.strip().startswith(("MCL", "Baker"))}
    assert float(row["MCL"].split()[-1]) < 0.05, "the chance arm kept weight on MCL"
    assert float(row["Baker's"].split()[-1]) > 0.85, "the strong arm was not given Baker's"
