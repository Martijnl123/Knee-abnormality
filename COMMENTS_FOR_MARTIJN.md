# Comments for Martijn

**Written 2026-09-15, last revised 2026-09-17 after E117.** Everything here has
a date on it because several numbers in this repo decay on their own — a rank in
particular. If this header is more than a few days old, re-pull the leaderboard
before trusting the priorities.

---

## 1. Where we actually are

| | |
|---|---|
| **Board** | **0.940** (2026-09-16) |
| Top of board | 0.957 |
| **Submissions** | **5/day, and today we have used ZERO** |
| **Our GPU quota** | **3.40 h left, refreshing 2026-09-19** |
| Team merge deadline | 2026-10-15 |
| Final submission | 2026-10-22 |

**SUBMISSIONS ARE NOT THE CONSTRAINT, AND THIS IS THE THING TO UNDERSTAND BEFORE
ANYTHING ELSE.** We have five today and nothing that deserves one. Four of the
last five submissions returned a number inside the reseed floor, which is another
way of saying **we are no longer short of board attempts — we are short of things
worth putting on the board.** What is actually scarce is **GPU hours** and
**ideas that survive a clean instrument**.

**Standing still is losing ground.** The rank moved 38 places overnight once with
no change to our score, because 46 teams joined and passed us. **The wall above is
dense**: ~837 teams at ≥0.938, 706 at ≥0.940, but only **81 at ≥0.945**. It is a
cliff at about 0.943, not a slope.

**The four-submission 2×2 is the most useful thing we have learned about this
board**, and it fell out of submissions spent on other questions:

| | blend 0.40 / 0.43 | blend 0.50 |
|---|---:|---:|
| **five v1 members** | 0.938 | 0.938 |
| **six v1 members** | **0.940** | **0.940** |

**Member count moved the board +0.002 twice. Blend weight moved it 0.000 twice.**
Neither margin escapes the ±0.003 reseed floor (E092), so nothing is *resolved* —
but a margin reproduced under a nuisance change is better evidence than a single
one, and a null reproduced under two member counts is a firmer null. **Adding
members is the only operation that has ever moved this board.**

**`docs/EXPERIMENTS.md` is the only current document.** Read backwards from
**E117**. `PATH.md`'s header is current; the rest of `docs/` is older than the
standing score.

---

## 2. What we are submitting, exactly

One kernel: **`knee-infer-raptorv1`** (`kaggle/86_infer_raptorv1/`). Two arms,
rank-blended **50/50**:

- **Four CC0 CoAtNet arms** from `dreaddevelopment` at the blend weights their
  authors published (0.55 / 0.20 / 0.15 / 0.10), from **three** distinct
  checkpoints. Alone: board 0.932.
- **Five full-fit resnet34** 2.5D models of ours at 192px. Alone: board 0.926.

**Both of those numbers are back to five members and the scalar 0.50 after two
pre-registered reverts fired** (E111 and E116, §9b). The banked 0.940 is
unaffected — the board keeps a team's best — so the reverts cost nothing and buy
a manifest that does not claim more than it has shown.

Everything mounted is CC0. The licence audit is E043/E088/E100.

---

## 2b. Can you submit for us? Almost certainly not usefully — here is why

**If you are already on our Kaggle team**, you share the same 5/day. You add no
submissions at all, and we are not using the ones we have.

**If you are on a separate team**, your submissions score *your* leaderboard, not
ours, until a merge — and Kaggle caps a merged team's combined submission count,
so submitting speculatively before merging can cost us the ability to merge at
all. **Merge deadline is 2026-10-15.** Please do not burn submissions on a
separate team on our behalf without checking that cap first.

**What you can actually add is GPU.** Your weekly quota is a separate ~30 h from
ours, and ours is the binding constraint right now: **3.40 h left until 19 Sep,
and the one job that is ready to run needs ~3.5 h.** §7 says what to run.

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

## 3b. READ THIS FIRST — E113 changed what §4 says (2026-09-16)

An outside research review pointed out, and **our own numbers confirm**, that the
CC0 CoAtNet checkpoints were trained on the **full** 4,407-study training set. So
their predictions on the 4,349 "non-gold" studies are **in-sample**, not
out-of-fold. The test needs no new data — our v1 arm is honestly out-of-fold on
both sets, so the gap between the halves should inflate where CoAtNet is
in-sample:

| study set | CoAtNet status | gap over our v1 |
|---|---|---:|
| 4,349 non-gold | **in-sample** | **0.0756** |
| 58 gold | held out | **0.0243** |
| **the board** | nothing in-sample | **0.0060** |

**12.6× from board to fit set.** And the middle row matters just as much:
published checkpoints carry a `gold_auc` field, so upstream had our 58 studies
and may have selected on them — gold-58 is not clean for CoAtNet either, only
cleaner.

**Working rule: for any comparison involving the CoAtNet arm, the board is the
only clean instrument.** E108's span conclusion is withdrawn, E112's validation
is void, and every "member gap" number in the log involving CoAtNet is inflated.
The v1 lineage is clean throughout.

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

## 6. What was open here is closed — E109 landed, and §7 supersedes this

**This section described E109 as in flight on 2026-09-15. It has since landed and
four more experiments have run on top of it (E114–E117).** Rather than rewrite a
section whose conclusions moved, the live picture is **§1** for where we stand and
**§7** for what to do; `docs/EXPERIMENTS.md` from E117 backwards is the record.

The one delivered finding from E109 that is still in use: **`input_norm=False`
measured −0.0064 on this lineage**, and every v1 member ships with it off.

## 7. If you want to spend GPU, in the order I would spend it

**1. THE RESEED CONTROL. ~3.5 GPU-h, and it is the only experiment currently
ready to run.** Retrain the sixth v1 member — the full-fit resnet50, same labels,
same geometry, `input_norm=False` — **with a different seed**, and blend it the
same way. E092 built the ±0.003 floor by changing nothing but the RNG seed and
watching 0.926 become 0.923/0.921. This separates *+0.002 of member* from *+0.002
of draw*, and it settles **E111 and the whole 2×2 in §1 at once**. We cannot run
it: quota is 3.40 h and it needs ~3.5 h. **If you have quota, run this.**

**2. More v1 members, if 1 comes back positive.** Member count is the only lever
with a measured board effect. If the sixth member survives its own reseed
control, a seventh and eighth are the cheapest thing on the board at ~1.5 GPU-h
each for resnet34.

**3. Rubric-aligned ordinal labels.** The one remaining structural idea. The
state ladder in `src/report_schema.py` is already ordinal and well built —
`absent / not_mentioned / equivocal / minimal / mild / moderate / severe` with
masked loss on silence — so the work is aligning `STATE_SCORE` to the
competition's own grading definitions, not inventing grading. LLM pass over 4,407
reports (no GPU), then a retrain (GPU).

**WHAT I WOULD NOT DO, and each of these is now a measurement rather than a
hunch:**

- **Do not mount more of `dreaddevelopment`'s bench (E117).** We screened six of
  the eleven untested CC0 checkpoints for 0.56 GPU-h. **Every one lands below
  every incumbent** — 0.9058 down to 0.8842 against 0.9116–0.9198 — and both
  weightings that can be justified without selection *lose*: all six at 0.25
  scores −0.0040, all six at 0.10 scores −0.0009 with CI [−0.0068, +0.0048].
- **Do not "just pick the good one" from that screen.** Added one at a time all
  six gain, +0.0007 to +0.0020. **That is the maximum of six draws from noise on
  58 studies with a ±0.006 paired interval**, and picking it is selecting on the
  test set — which is precisely E106's failure, later traced by E113 to reading
  memorisation. I left all six out on purpose.
- **Do not chase per-finding blend weights (E116).** We built a version that
  touches neither gold-58 nor CoAtNet's predictions, worth +0.0023 on held-out
  gold at P(better) 0.897, recovering 72% of the loss E105's oracle found on MCL.
  **The board returned 0.940 — exactly what the scalar returns.** The derivation
  is sound and shelved by a measurement; `one_sided_weights` is kept in
  `eda/per_finding_weights.py` with tests so it can be reinstated in one line.
- **Do not chase synovitis (E115).** It is a **label ceiling**, measured: our
  labels score 0.790 on it against our model's 0.779. Fracture is the control —
  labels 0.793, model 0.885. No public label set beats ours on synovitis.

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

## 9b. E111 and E116 both resolved, and both reverted on their own rules

**E111** took the v1 half from five full-fit resnet34 to six, the extra a full-fit
resnet50. Board: **0.938 → 0.940**, the best score this project has recorded. Its
own pre-registration said 0.936–0.940 is inside the ±0.003 floor and the rule is
**revert to five**. It has been reverted.

**E116** replaced the scalar blend weight with one weight per finding, derived
without touching gold-58 or CoAtNet. Board: **0.940 — the same number**, not a
worse one. Middle bracket, rule was revert. **Reverted.**

**The E111 revert was deliberately held back until E116 resolved**, because
firing it earlier would have made that submission a two-variable change against
the standing 0.940 with no way to read which half moved the board. Both fired
together once the number landed.

**Neither rule was renegotiated after seeing the result**, and that is the part
worth copying. The banked 0.940 stands whatever the manifest says next, so the
reverts cost nothing — and keeping a change the instrument cannot resolve is how
E083 cost a board point.

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
