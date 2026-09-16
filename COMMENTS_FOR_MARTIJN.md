# Comments for Martijn

**Written 2026-09-15 07:15 UTC.** Everything here has a date on it because
several numbers in this repo decay on their own — a rank in particular. If this
header is more than a few days old, re-pull the leaderboard before trusting the
priorities.

---

## 1. Where we actually are

| | |
|---|---|
| **Board** | **0.940** (submitted 2026-09-16, E111's six-member blend) |
| **Rank** | **688 of 3,839** — was 798 of 3,769 at 0.938 |
| Top of board | 0.957 |
| Submissions used | 22 total; 5/day, and we rarely use them |
| Final submission | 2026-10-22 |

**The rank moved 38 places overnight with no change to our score**, because 46
teams joined and passed us. That is the single most important thing to
understand about this leaderboard: standing still is losing ground.

**The wall above us is dense.** 837 teams at ≥0.938, 706 at ≥0.940, 537 at
≥0.941 — but only **81 at ≥0.945**. Between us and 0.945 there are ~720 teams in
0.007 of AUC. It is not a gentle slope; it is a cliff at about 0.943.

**Two documents in `docs/` are stale and will mislead you.** `PATH.md` says
0.932 and rank ~1,166 (dated 2026-09-08); `STATUS.md` was last updated
2026-09-07. **`docs/EXPERIMENTS.md` is current** — entries E092 through E109 are
the last two weeks and they are where the real state lives. Read backwards from
E109.

---

## 2. What we are submitting, exactly

One kernel: **`knee-infer-raptorv1`** (`kaggle/86_infer_raptorv1/`). Two arms,
rank-blended 50/50:

- **Four CC0 CoAtNet models** from `dreaddevelopment`, at the blend weights their
  authors published (0.55 / 0.20 / 0.15 / 0.10). Alone: board 0.932.
- **Five full-fit resnet34** 2.5D models of ours at 192px. Alone: board 0.926.

Together: **0.938**. The v1 arm is worth **+0.006**, which matters below.

Everything mounted is CC0. The licence audit is E043/E088/E100.

---

## 3. What is closed, and please do not re-open these

Nine routes, each closed on a **measurement**, not a hunch. The number in
brackets is the experiment.

| route | why it is dead |
|---|---|
| More public/foreign models (E098, E101) | Every arm we can legally reach scores **0.79–0.86** on our 58 expert studies against our CoAtNet's **0.92**. All blends decline monotonically from weight 0. |
| `pilkwang`'s 20 DINOv2 checkpoints (E105) | Its two published prediction files correlate **0.995** — the file we already scored at 0.8400 **is** that arm, ensembled. Running the weights would reproduce a measured negative. Saved ~3 GPU-h by reading a manifest. |
| RadImageNet (E100) | 0.8576, same dead band. The licence question (NonCommercial, not ShareAlike — E043 cited the wrong clause) turned out moot. |
| Public label sets (E089, E104) | Three surveyed, none beats what we train on. Training on `dreaddevelopment`'s 4,349-study set vs ours: **not separated**. |
| Test-time augmentation (E103, E105) | Ten of twelve variants correlate **>0.98** with their parent. The model attention-pools ~60 windows, so it is nearly invariant to these perturbations. Negative on top of the shipped blend. |
| Per-finding blend weights (E106) | Real headroom (+0.0076) exists and is **provably unreachable** — see §4. |
| Blend mixing weight (E107) | 0.40 vs 0.50 scored **identically to three decimals**. |
| Narrower inference span (E108) | Looked like a winner on 58 studies (+0.0055); on 4,349 it is **−0.0068**. Detail in §5 — it is the most instructive failure in the log. |
| Architecture (E012–E024) | **This one is being re-opened right now.** See §6. |
| Per-plane attribution (E110) | Looked like +0.082 across 5 of 12 findings; naming the plane from anatomy *before* looking scored **−0.0201** against pooling. Selection bias. Caveat: measured on frozen features under the old labels, so "unsupported", not "refuted". |

---

## 4. The three instruments, and what each can and cannot do

This is the part worth internalising. Most of our wasted effort came from
using the wrong judge.

**Gold-58** — the 58 studies with expert labels. Honest, and the only offline
thing correlated with the board. But n=58: its paired CI on a blend difference
is **±0.006 at best**, and it cannot fit anything with parameters. E107 gave it
the single easiest job it will ever get — one scalar, paired design, bootstrap
saying `P(optimum ≤ 0.50) = 0.972` — and the board saw nothing.

**Report labels (4,349 studies)** — 75× the sample, and its usability depends
entirely on *what you compare*:

- **Across architectures: worse than useless.** Asked to weight our v1 arm
  against CoAtNet, its optimum was to **delete the v1 arm** — the arm worth
  +0.006. Its per-finding preferences correlate **+0.052** with what gold wants.
  *Mechanism*: the public arms were trained toward LLM-parsed report labels, so
  scoring them on report labels rewards agreement with what they were fitted to,
  and our arm earns its gain exactly where it departs from that consensus.
- **Within one checkpoint family: works, at +0.800.** The bias is common-mode
  between two inference geometries of the same weights, so it cancels (E108).

**The board** — 5/day, ~2h15m latency, and the only ground truth. It keeps your
**best** submission, so **a submission can never cost you anything**. We under-use
this. The floor is ±0.003 (E092, a pure reseed).

**Do not convert offline gains to board gains with a fixed ratio.** We measured
1.6× and 2.0×, both on *adding a member* to a blend. Applied to a *mixing weight*
change it predicted 0.941 and the board printed 0.938 (E107).

---

## 5. The failure I would most want you to read: E108

E103 tested six narrowed-span variants of our CoAtNet arms on gold-58. **All six
beat their parent.** Six for six, one direction — it reads as p ≈ 0.016. One of
them, `maxspan-v5-span04` at **0.9253**, is still the highest single arm this
project has ever measured, above the published four-arm blend itself.

Shipping it was the obvious move. On 4,349 studies all three tested variants
come back **−0.0068, −0.0062, −0.0119**, with intervals an order of magnitude
tighter. **Opposite sign.**

Why the six-for-six was not evidence: six variants of three checkpoints, all
scored on the same 58 studies. That is **one correlated fluctuation read six
times**, not six independent votes. The lesson is not "n=58 is noisy" — it is
that repeating a comparison across variants of the same thing on the same small
sample manufactures confidence without adding information.

Gold-58 would have congratulated us the whole way into a worse submission.

---

## 6. What is open right now — E109, running as you read this

`PATH.md` §1 says *"architecture, every attempt: 0.000"*, and that line governs
how every GPU hour here gets spent. **Every experiment behind it ran on or before
2026-08-19** — and then E041/E044 changed the labels for **+0.1067 on gold**.

So the claim was measured under labels costing 0.107 of macro AUC, which is
**three times E060's own ±0.03 noise floor**. An architecture effect could not
have been seen through that. And E020's own entry disowns itself: *"0.6878 is not
a measurement of this backbone; it is where the clock stopped."*

**Three arms, fold 0, ~4 GPU-h:**

| kernel | backbone | input_norm | seed |
|---|---|---|---|
| `knee-train-v1pub` (exists) | resnet34 | False | — |
| `knee-train-v1pub-norm` | resnet34 | **True** | 3 |
| `knee-train-v1pub-cnx` | **convnext_tiny** | True | 3 |

The third arm exists because convnext needs ImageNet normalisation and our
resnet34 baseline trained without it — comparing them directly confounds backbone
with input scaling, which is **exactly** what E020 flagged in August and never
separated. Backbone reads from the two normalised arms. The normalisation reading
is seed-confounded and that is recorded up front, not discovered later.

**Read it on fold 0's 882 held-out studies, not the ~12 gold ones a single fold
carries.** That is why this probe is readable when every previous one-fold
architecture probe was not.

**Caveat stated before the result:** report labels for *two of our own models,
same labels, same fold, different backbone* is an **untested middle case** between
the +0.800 and +0.052 regimes above. The bias argues it cancels. It has not been
measured for this class.

**OUTCOME (2026-09-15): the primary question was NOT answered.** The convnext arm
failed twice — CUDA OOM at batch 16, then a host `Killed` at batch 4 with no
traceback, undiagnosed. **`convnext_tiny` does not run in this harness and I do
not know why.** The control ran fine at batch 16 on the identical loader, so it
is the model, not the data path.

**The architecture claim is therefore still UNTESTED, not confirmed.** A failed
run is not evidence a claim survived. If you pick this up, use **`resnet50` via
torchvision** rather than convnext — it avoids the timm path entirely, and
same-family means normalisation stops being a confound.

**The control did settle E020's other confound**, which is worth having:
ImageNet normalisation **hurts** this lineage by **−0.0064** on fold 0's 882
studies, CI [−0.0113, −0.0014], P(better) = 0.006. Seed-confounded (incumbent
`seed=None` vs control `seed=3`), so the direction is supported and the magnitude
is not clean. It means E020's DINOv2 arm carried a measured handicap its resnet34
arm did not.

*(The convnext arm OOMed on the first attempt at batch 16 — 3 planes × 20 slices
= 60 images per study. Refixed as batch 4 × 4 accumulation, the same effective
16. Exactly equivalent here rather than approximately, because convnext uses
LayerNorm, which is per-sample.)*

---

## 7. If you want to spend GPU, in the order I would spend it

1. **Wait for E109.** ~4 GPU-h already committed. If convnext separates, five
   folds is the obvious follow-up and the architecture route is alive for the
   first time.
2. **Submit more.** We have used 22 submissions in two weeks against a 5/day
   allowance and the board keeps our best. Anything with an argument behind it
   should just be tested — the cost really is zero.
3. **A genuinely stronger third arm.** The blend is two arms. Every public third
   arm is too weak (§3). Training one at CoAtNet quality is ~20 GPU-h against a
   project history where architecture measured zero — but §6 is exactly the
   question of whether that history is real.

**What I would not do:** chase the +0.0076 of per-finding headroom. It is real
and we have proven no instrument can find it — gold-58 cannot fit 12 parameters
on 58 studies, and the only larger arbiter is anti-correlated for that
comparison class (E106).

---

## 8. Operational things that will trip you up

- **`kaggle competitions submit` does not work** for this competition — HTTP 400,
  notebook-only. **Every submission needs a human clicking Submit** on the
  notebook page. Do not debug the CSV; it is not the CSV.
- **Never hand-edit `kaggle/*/run.py`.** They are generated from `src/pipeline.py`
  by `python eda/generate_kernels.py --write`. A drift check enforces this.
- **Run `bash eda/preflight.sh` before every push.** Lint, tests, kernel drift,
  and a check that no patient-derived file is tracked.
- **Commit attribution must be `existentialistlogarithmic
  <achilleasd278@gmail.com>` in both the author field and `Co-Authored-By`.** The
  container's git defaults are wrong; set them explicitly on the command.
- **Kaggle allows 2 concurrent GPU sessions.** `bash eda/push_queue.sh <dirs>`
  queues past that.
- **CPU kernels cost no GPU quota.** The out-of-fold evals (`gold_eval` template)
  are deliberately CPU for that reason.

---

## 9. The method, in one paragraph

Pre-register what a result would have to look like *before* the data arrives, and
then honour it even when it is inconvenient — E107's weight was reverted on its
own rule, and E108 closed a route that gold-58 was still endorsing. Every claim
carries its interval. A negative needs a control arm; E060 exists because one
did not have one. And a closure has a **date**: three claims in this log were
true when written and false later (E046, E070, and §6's architecture line), so
anything load-bearing gets re-read rather than inherited.

If a number here matters to a decision you are about to make, check when it was
measured before you use it.

---

## 9b. In flight right now (E111)

The blend's v1 half is being taken from five full-fit resnet34 to **six**, the
extra one a full-fit **resnet50** — same labels, same geometry, different depth.

It ships **without an offline number and cannot have one**: a full-fit model
trains on all 58 gold, so its gold score is memorisation. The justification is
narrow — the board keeps our best submission and 0.938 is banked, so being wrong
costs one click. It is not a general licence to ship blind.

`input_norm=False` on that arm is **E109's one delivered finding being used**:
normalisation measured −0.0064 on this lineage.

Expect the middle bracket. E064 priced extra same-lineage members at +0.001, and
a depth change is more than a reseed and less than a new family. If the board
reads 0.936–0.940 the correct move is **revert to five**, because five needs no
justification.

---

## 10. One thing that is NOT in main, on purpose

`origin/rsna-knee-abnormality-pipeline` is an abandoned branch from 2026-08-20
with 5 commits that never merged. Its code is **deliberately not merged** — it
diverged before most of the current pipeline existed and produces 8 conflicts in
files rewritten many times since.

Its one finding that `main` lacked has been **ported as text** (E110, the plane
attribution result), and the tool that produced it,
`eda/plane_ablation.py`, exists **only on that branch**. If you ever want to
re-test per-plane heads on the current features and labels, get the tool from
there rather than rewriting it — but do not merge the branch.
