#!/usr/bin/env python3
"""Per-finding blend weights, fitted off-gold and tested on gold (E106).

    python eda/per_finding_weights.py \
        --coat  artifacts/trainall_probs.parquet \
        --v1    artifacts/oof_all_fold*.json \
        --labels artifacts/llm_labels_v4_blend.csv \
        --gold  artifacts/train.csv

**The one thing this file exists to protect.** Six schemes in `EXPERIMENTS.md`
were refused for choosing a blend weight on the 58 expert studies and then
reporting the result on those same 58. The weights here are derived on the
**4,349 non-gold studies** against the public report labels, and the 58 are only
ever used to *score* the finished rule. If a future edit lets gold rows reach
`fit_weights`, the validation becomes circular and the number it prints stops
meaning anything — so the split is asserted, not documented.

**The formula has no free parameters, deliberately.** Skill above chance,
normalised:

    s_x(f) = max(0, AUC_x(f) - 0.5)
    w_v1(f) = s_v1(f) / (s_v1(f) + s_coat(f))

A threshold, a shrinkage coefficient or a floor would each be a number chosen by
someone who had already seen the answer, which is the whole failure mode.
Degenerate case: if neither arm beats chance on a finding the denominator is
zero, and the weight falls back to 0.5 — no information, so no opinion.

**The arbiter's defect, stated here rather than in a commit message.** The report
labels are a proxy: E041 measured them at 0.8927 macro against the 58 experts,
and E093 found the proxy's validity unverified (gap spans 0.181, Spearman
0.573). They carry 75x the sample of gold-58 and, unlike gold-58, leave an honest
test set. If the rule loses, "the proxy does not transfer" and "the rule is bad"
are not separable from this script's output alone.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FINDINGS = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",
            "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",
            "Contusion", "Fracture"]
PUBLISHED_ARM_WEIGHTS = {"maxspan-v5": 0.55, "native384dense-v10": 0.10,
                         "maxspan-v5-reverse": 0.15, "native384-v8": 0.20}

# Our arm's honest out-of-fold AUC per finding on the 4,349 non-gold studies,
# against its own training labels. A table of measurements, not of choices --
# it is the sole input to `one_sided_weights` below. Published in E116 rounded
# to three decimals, which is why reproducing the shipped vector from it lands
# three of twelve columns one unit off in the last place.
V1_OOF_AUC_E116 = {
    "ACL": 0.825, "MCL": 0.778, "Medial Meniscus": 0.900,
    "Lateral Meniscus": 0.864, "Medial OA": 0.865, "Lateral OA": 0.810,
    "PF OA": 0.804, "Effusion": 0.826, "Synovitis": 0.823,
    "Baker's": 0.889, "Contusion": 0.841, "Fracture": 0.862,
}


def auc(y, p):
    """Mann-Whitney AUC with average ranks for ties.

    Written out rather than imported so the tests pin this repo's own
    arithmetic; matches `sklearn.metrics.roc_auc_score` including heavy ties.
    """
    y = np.asarray(y, np.float64)
    p = np.asarray(p, np.float64)
    npos, nneg = float((y == 1).sum()), float((y == 0).sum())
    if npos == 0 or nneg == 0:
        return float("nan")
    order = np.argsort(p, kind="mergesort")
    ranks = np.empty(len(p), np.float64)
    ranks[order] = np.arange(1, len(p) + 1, dtype=np.float64)
    ps = p[order]
    i = 0
    while i < len(ps):
        j = i
        while j + 1 < len(ps) and ps[j + 1] == ps[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return float((ranks[y == 1].sum() - npos * (npos + 1) / 2.0) / (npos * nneg))


def rankpct(x):
    order = np.argsort(x, axis=0, kind="mergesort")
    out = np.empty(x.shape, np.float64)
    for k in range(x.shape[1]):
        out[order[:, k], k] = np.arange(x.shape[0])
    return out / max(1, x.shape[0] - 1)


def fit_weights(truth, coat, v1, gold_mask=None):
    """One weight per finding, from skill above chance on the FIT set.

    `gold_mask` is not a convenience: pass it and any True row is refused. The
    caller has already excluded them; this is the assertion that they stayed
    excluded through whatever reindexing happened in between.
    """
    if gold_mask is not None and np.any(gold_mask):
        raise ValueError(
            f"{int(np.sum(gold_mask))} gold studies reached the weight fit. "
            "The 58 are the test set; fitting on them makes the validation "
            "circular and every number downstream meaningless.")
    weights, table = [], []
    for k, finding in enumerate(FINDINGS):
        a_c, a_v = auc(truth[:, k], coat[:, k]), auc(truth[:, k], v1[:, k])
        s_c, s_v = max(0.0, a_c - 0.5), max(0.0, a_v - 0.5)
        w = 0.5 if (s_c + s_v) == 0 else s_v / (s_c + s_v)
        weights.append(w)
        table.append({"finding": finding, "auc_coat": a_c, "auc_v1": a_v, "w_v1": w})
    return np.array(weights), pd.DataFrame(table)


# E116's SHIPPED RULE. `fit_weights` above is E106's, and E113 established why it
# cannot be used: `auc(truth, coat)` scores CoAtNet against report labels on the
# 4,349, and CoAtNet was TRAINED on those studies, so that term reads
# memorisation rather than skill. Any weight vector derived from it is the
# E106 failure again. It is kept because E106's entry refers to it, NOT because
# it is live -- do not paste its output into the manifest.
#
# The rule that ships touches CoAtNet nowhere. It weights our own arm per finding
# by how well that arm learned ITS OWN supervision -- honest out-of-fold AUC
# against its own training labels -- and is one-sided: learning your own labels
# well is not evidence you beat the other arm, so nothing rises above 0.50 and
# only reductions happen. The reference is the best-learned column, a datum in
# the data rather than a constant someone chose.
#
# RECONSTRUCTED AFTER THE FACT, and the reconstruction is checked rather than
# asserted: `tests/test_per_finding_weights.py` re-derives the twelve numbers the
# manifest ships from the AUC table published in E116 and pins them. Nine match
# to the last digit; three land one unit off in the third decimal because the
# published table is rounded to 3 dp and the original derivation ran on
# full-precision AUCs. That is the expected signature of rounding, and it is
# recorded here rather than smoothed over.


def one_sided_weights(auc_v1):
    """w_v1(f) = 0.5 * (AUC_v1(f) - 0.5) / (max_f AUC_v1(f) - 0.5).

    `auc_v1` maps finding -> our arm's honest out-of-fold AUC. Returns weights in
    FINDINGS order. No CoAtNet term, no gold-58, no free parameter.
    """
    missing = [f for f in FINDINGS if f not in auc_v1]
    if missing:
        raise ValueError(f"no out-of-fold AUC for {missing}")
    a = np.array([float(auc_v1[f]) for f in FINDINGS])
    if np.any(a <= 0.5):
        raise ValueError(
            "an arm at or below chance on "
            f"{[FINDINGS[k] for k in np.flatnonzero(a <= 0.5)]} has no skill to "
            "scale; the one-sided rule has nothing to say and a weight would be "
            "invented rather than derived.")
    best = a.max()
    return 0.5 * (a - 0.5) / (best - 0.5)


def blend(coat, v1, w_v1):
    """Rank-blend with a per-finding weight. `w_v1` may be a scalar."""
    rc, rv = rankpct(coat), rankpct(v1)
    w = np.broadcast_to(np.asarray(w_v1, np.float64).reshape(1, -1), rc.shape)
    return (1.0 - w) * rc + w * rv


def macro(truth, pred):
    per = [auc(truth[:, k], pred[:, k]) for k in range(truth.shape[1])]
    return float(np.nanmean(per)), per


def load_v1_oof(patterns):
    rows = {}
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            d = json.loads(Path(path).read_text())
            if d["findings"] != FINDINGS:
                raise SystemExit(f"{path} has a different finding order")
            for study, pred in zip(d["studies"], d["predicted"], strict=True):
                rows[str(study)] = pred
    return rows


def load_coat(path):
    frame = pd.read_parquet(path)
    frame["StudyInstanceUID"] = frame["StudyInstanceUID"].astype(str)
    missing = set(PUBLISHED_ARM_WEIGHTS) - set(frame["arm"].unique())
    if missing:
        raise SystemExit(f"dump is missing arms {sorted(missing)}")
    return frame


def coat_column(frame, ids):
    """Upstream's published per-arm weights, rank-averaged. Nothing fitted."""
    total = sum(PUBLISHED_ARM_WEIGHTS.values())
    out = None
    for arm, weight in PUBLISHED_ARM_WEIGHTS.items():
        block = frame[frame.arm == arm].set_index("StudyInstanceUID")
        part = rankpct(block.loc[ids, FINDINGS].to_numpy(np.float64)) * (weight / total)
        out = part if out is None else out + part
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coat", required=True, help="trainall_probs.parquet")
    parser.add_argument("--v1", required=True, nargs="+", help="oof_all_fold*.json")
    parser.add_argument("--labels", required=True, help="report labels CSV (the arbiter)")
    parser.add_argument("--gold", required=True, help="competition train.csv")
    args = parser.parse_args(argv)

    train = pd.read_csv(args.gold)
    train["StudyInstanceUID"] = train["StudyInstanceUID"].astype(str)
    is_gold = train[FINDINGS].notna().all(axis=1)
    gold_ids = train.loc[is_gold, "StudyInstanceUID"].tolist()
    gold_truth = train.loc[is_gold, FINDINGS].to_numpy(np.float64)
    print(f"gold studies (TEST set, never fitted on): {len(gold_ids)}")

    labels = pd.read_csv(args.labels)
    labels["StudyInstanceUID"] = labels["StudyInstanceUID"].astype(str)
    labels = labels.set_index("StudyInstanceUID")

    coat_frame = load_coat(args.coat)
    v1_rows = load_v1_oof(args.v1)

    have = set(coat_frame.StudyInstanceUID) & set(v1_rows) & set(labels.index)
    fit_ids = [s for s in train.StudyInstanceUID if s in have and s not in set(gold_ids)]
    print(f"fit studies (non-gold, report-labelled): {len(fit_ids)}")

    # The arbiter is soft; AUC needs a class. 0.5 is the natural cut for a
    # probability and is not tuned — a tuned threshold would be a free parameter.
    fit_truth = (labels.loc[fit_ids, FINDINGS].to_numpy(np.float64) >= 0.5).astype(float)
    # A finding with one class on the fit set has an undefined AUC, which would
    # make its weight nan and poison the blend for that column. Name them loudly
    # rather than letting a nan propagate into a submission.
    single = [FINDINGS[k] for k in range(len(FINDINGS))
              if fit_truth[:, k].min() == fit_truth[:, k].max()]
    if single:
        raise SystemExit(
            f"single-class findings on the fit set: {single}. Their AUC is "
            f"undefined, so no weight can be derived and the blend would carry "
            f"a nan column into a submission.")

    fit_coat = coat_column(coat_frame, fit_ids)
    fit_v1 = np.array([v1_rows[s] for s in fit_ids], np.float64)
    weights, table = fit_weights(fit_truth, fit_coat, fit_v1,
                                 gold_mask=np.isin(fit_ids, gold_ids))
    print("\nweights fitted on the report labels, NOT on gold:")
    print(table.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    gold_coat = coat_column(coat_frame, gold_ids)
    gold_v1 = np.array([v1_rows[s] for s in gold_ids], np.float64)
    uniform, _ = macro(gold_truth, blend(gold_coat, gold_v1, 0.5))
    fitted, per = macro(gold_truth, blend(gold_coat, gold_v1, weights))
    print(f"\nHELD-OUT 58 — uniform 0.5      {uniform:.4f}")
    print(f"HELD-OUT 58 — fitted weights   {fitted:.4f}")
    print(f"                    difference {fitted - uniform:+.4f}   "
          f"(E106 rule 1 ships only above +0.0030)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
