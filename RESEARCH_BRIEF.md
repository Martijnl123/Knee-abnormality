# Research brief: RSNA Knee Abnormality Detection — how to get from 0.940 to 0.945+

**Paste this whole file into Claude Research.** It is a self-contained statement
of a Kaggle competition, what has been tried, what was measured, and the specific
questions worth researching. Everything below is measured unless flagged.

---

## The ask

We are at **0.940** public LB, rank **688 / 3,839**. We want **0.945+**, which is
rank ~86, the top 2.2%. **We need +0.005 and have exhausted every route we could
think of.** Tell us what we are missing — ideally from published literature or
from what winning solutions in comparable medical-imaging competitions actually
do.

**We are not looking for a list of standard ideas.** Sections 4 and 5 list what
we already tried and the number it returned. Please read those before answering,
and say explicitly if you are re-proposing something we closed and why you think
our test was wrong.

---

## 1. The competition

- **Task**: 12 binary findings per knee MRI study (ACL, MCL, Medial/Lateral
  Meniscus, Medial/Lateral/PF OA, Effusion, Synovitis, Baker's cyst, Contusion,
  Fracture).
- **Metric**: **macro ROC-AUC over the 12 findings.** Threshold-free, so
  calibration is a no-op. Every finding is weighted equally, which matters: our
  weakest (Synovitis 0.809) has far more headroom than our strongest (Effusion
  0.984).
- **Data**: 4,407 training studies, each with multiple DICOM series across
  sagittal / coronal / axial planes. Hidden test ~1,300 studies.
- **Labels**: the training set ships **radiology report text**, not per-finding
  labels. Only **58 studies** carry expert per-finding labels. Everyone in the
  field derives training labels by LLM-parsing the reports. **No report text
  exists at test time.**
- **Format**: notebook-only code competition, 9h runtime cap, 5 submissions/day,
  ends 2026-10-22.

## 2. The leaderboard shape — this is the important context

```
score    teams at or above
0.957      1      (top)
0.950     38
0.945     86     <- our target, top 2.2%
0.943    134
0.941    616     <- a cliff: 482 teams between 0.941 and 0.943
0.940    792
0.938    924
```

**There is a wall at ~0.941 and a cliff at ~0.943.** Roughly 600 teams sit within
0.003 of us. The public-notebook fork crowd lands at 0.936–0.941. **Whatever the
top 134 teams are doing is qualitatively different, and we cannot see it.**

That is the central question: **what separates 0.943+ from the 0.941 plateau in a
competition of this shape?**

## 3. Our current system (0.940)

A rank-mean blend, 50/50, of two halves:

**Half A — four CoAtNet arms (0.932 alone).** Public CC0 checkpoints from another
competitor (`coatnet_rmlp_2_rw_384`), run at their published geometry: a fixed
slot layout over plane/fluid-sensitivity combinations, 336–384px, a 140mm
physical crop, ~62 three-slice windows per study, attention-pooled per finding.
Four arms from three checkpoints at published weights 0.55 / 0.20 / 0.15 / 0.10.

**Half B — six full-fit resnet34/50 (0.926 alone).** Our own 2.5D model: 3 planes
× 20 slices at 192px / 0.6mm, a 2D backbone over slices, attention-pooled to a
study, 12 heads. Trained on LLM-parsed report labels.

**Measured on our 58 expert studies:** CoAtNet half 0.9223, our half 0.8980,
blend 0.9254. Cross-architecture rank correlation **0.793**.

## 4. What we measured about our own instruments (read this before proposing evaluation)

This is the part we would most like challenged, because it constrains everything.

- **58 expert studies** is our only honest offline instrument. Paired CI on a
  blend difference is **±0.006 at best**; absolute CI is ±0.0153. It cannot fit
  parameters.
- **Report labels on 4,349 non-gold studies** — 75× the sample — are
  **anti-informative across architectures**: asked to weight our arm against the
  CoAtNet arm, the optimum was to **delete our arm**, the one worth +0.006 on the
  board. Its per-finding preferences correlate **+0.052** with what the expert
  labels want. *Mechanism*: the public models were themselves trained toward
  LLM-parsed report labels, so scoring them on report labels rewards agreement
  with what they were fitted to, and our arm earns its gain exactly where it
  departs from that consensus.
- **The same report labels ARE usable within one checkpoint family** (+0.800
  agreement) — the bias is common-mode between two inference geometries of the
  same weights.
- **The board's own floor is ±0.003**, established by a pure reseed (same
  config, different RNG: 0.926 → 0.923 / 0.921).
- **Gold→board transfer ≈ 1.6–2.0×** for *adding a member* to a blend, and
  **does not apply to re-mixing members already present** (predicted 0.941 for a
  weight change; board printed 0.938).

**Question for you: is there a better offline instrument we are missing?** With
58 expert labels and 4,349 noisy proxy labels, is there a published approach to
model selection that we should be using — noisy-label-aware validation, some form
of agreement-based ranking, anything?

## 5. What we tried and what it returned — please do not re-propose without cause

| route | result |
|---|---|
| Other public/foreign models (5 systems) | all score **0.79–0.86** on our 58 vs our CoAtNet's 0.92; every blend declines monotonically from weight 0 |
| The field's most-mounted CC0 asset (20× DINOv2-small) | its own published predictions read **0.840**; blending measured negative |
| RadImageNet arm | 0.8576, same dead band |
| Public LLM label sets (3 surveyed) | none beats the one we use; training on a different 4,349-study set: **not separated** |
| Test-time augmentation (12 variants) | 10 of 12 correlate **>0.98** with their parent; negative on top of the shipped blend |
| Per-finding blend weights | oracle headroom is **+0.0076** and **provably unreachable** — 58 studies can't fit 12 params, and the larger arbiter is anti-correlated |
| Blend mixing weight 0.5 → 0.4 | **0.938 both ways**, identical to 3 decimals |
| Narrower inference crop | looked like **+0.0055** on 58 studies; on 4,349 it is **−0.0068**. Opposite sign |
| Re-fitting the CoAtNet arm weights off-gold | +0.0024 on held-out, below our bar |
| A 6th ensemble member (resnet50) | 0.938 → **0.940**, i.e. **+0.002, inside the ±0.003 floor** |

**One live sub-finding**: the `maxspan-v5-reverse` arm correlates **0.986** with
its own parent and an independent fit drives its weight from 0.15 to **0.021**.
Upstream's blend carries a member that contributes ~nothing.

## 6. Constraints

- ~30 GPU-h/week on 2× T4 (16GB), currently spent. 9h cap per run.
- Submissions are free and the board keeps our best, so **anything with an
  argument behind it can just be tested**.
- Licensing: CC0 and Apache assets only. One key asset (a DINOv3 repro set) has
  **no licence grant** and is excluded. RadImageNet is CC-BY-NC-SA; ShareAlike
  doesn't bite for inference-only use, but NonCommercial is a live question for a
  prize competition.
- We will not fit parameters on the 58 expert studies. We have declined this
  seven times and been right each time.

## 7. The specific questions

1. **What do teams at 0.943–0.957 plausibly have that a 0.941 plateau team does
   not**, in a competition with report-derived labels and a tiny expert set?
   Is the gap architecture, label quality, ensembling scale, or something
   structural we have not considered?
2. **Label quality is our largest measured lever** (+0.107 from switching label
   sets, and the strongest public write-up says the same: "better labels > bigger
   models"). Is there published work on extracting better structured labels from
   free-text radiology reports than a single-pass LLM — multi-pass, ensemble
   labellers, uncertainty-aware labelling, VisualCheXbert-style
   image-conditioned relabelling?
3. **Macro-AUC with 12 unequal findings**: is there published work on optimising
   *macro* AUC specifically — per-class loss weighting, AUC-margin losses,
   class-balanced sampling — that reliably beats plain BCE on the weak classes?
4. **Our weak findings are Synovitis (0.809), Lateral OA (0.845), PF OA (0.842).**
   Is there anatomical/MRI-sequence knowledge that says these need a specific
   plane, sequence, or resolution we may be discarding? Our 2.5D model pools
   3 planes × 20 slices at 192px, which may be too coarse for subtle findings.
5. **Ensembling**: we have 2 strong arms at correlation 0.793. Published 0.937
   systems use 4 arms / 39 models. Is there evidence on how many decorrelated
   arms it takes to move macro AUC by 0.005 at this level, and whether the
   returns are worth the compute?
6. **Is there anything about MRI-specific preprocessing** — intensity
   normalisation across scanners, bias-field correction, sequence-aware
   handling, registration — that medical-imaging competition winners routinely do
   and we are not?

## 8. What a useful answer looks like

Concrete, cited where possible, and honest about effect sizes. We have a
disciplined measurement setup and will test what you propose properly — so a
ranked list of 3–5 mechanisms with expected magnitude and cost beats twenty
generic suggestions. **If your honest read is that 0.945 requires compute or data
we do not have, say that.**
