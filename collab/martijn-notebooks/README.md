# Martijn — six notebooks, in order

Everything here is **already configured for your account** (`martijnlustig`).
You do not edit any code. Each folder has:

- `run.py` — paste this in as the whole notebook
- `kernel-metadata.json` — reference only; it records the settings listed below

**Only notebook 6 uses GPU.** The first five are CPU and cost none of your
30 GPU-h/week.

---

## STEP 0 — join the competition. Nothing works before this.

Go to the competition page → **Join Competition** → accept the rules.

Until you do, the competition does not appear in Kaggle's "Add Input" list, and
any notebook that tries to read it fails with **`competition data not found under
/kaggle/input`**. That is the script failing loudly rather than producing an empty
scan, and it is the first thing everyone hits. You need to have joined before any
team merge anyway.

To check it worked, run this one line in any notebook with the competition
attached:

```python
import subprocess
print(subprocess.run(["ls","/kaggle/input"], capture_output=True, text=True).stdout)
```

Empty output means the competition is not attached, or not joined.

---

## Two ways to run this

**A. In the browser** — six notebooks, click by click. Everything below. No API
token needed at all.

**B. From your own machine** — `setup_and_run.sh` in this folder does the CPU
stages and waits for them:

```bash
export KAGGLE_API_TOKEN=...           # in YOUR shell only
export KAGGLE_PUSH_ACCOUNT=martijnlustig
bash setup_and_run.sh
```

It stops before the GPU stage on purpose, so you can look at a cache log before
spending 3.5 h of quota.

**Your token stays in your shell in both cases.** Do not paste it into a chat
window, an AI prompt, or a file you send to anyone — including us. Nothing in this
folder needs it from anyone but you. If a token has already been pasted somewhere,
expire it: Kaggle → Settings → API → **Expire API Token**.

---

## Which files to grab

**Six separate Kaggle notebooks, one per folder.** You paste six files in total:

```
00_dicom_header_scan/run.py        -> notebook 1
03_cache_build_shard0/run.py       -> notebook 2
03_cache_build_shard1/run.py       -> notebook 3
03_cache_build_shard2/run.py       -> notebook 4
03_cache_build_shard3/run.py       -> notebook 5
97_train_v1pubfull_r50/run.py      -> notebook 6
```

Ignore the `kernel-metadata.json` files — they are reference only, recording the
settings that are written out below. Nothing in them gets pasted anywhere.

**THE ONE THING THAT WILL SILENTLY GO WRONG.** The four `03_cache_build_shard*`
scripts look identical — same length, same code — but each carries a different
line 57:

```
RUN_SHARD           = 0      <- shard0/run.py
RUN_SHARD           = 1      <- shard1/run.py
RUN_SHARD           = 2      <- shard2/run.py
RUN_SHARD           = 3      <- shard3/run.py
```

**Paste each one from its own folder.** If you copy the same script into all four
notebooks, all four build quarter 0, three quarters of the cache never gets built,
and nothing complains until the trainer is missing most of its data. **After
pasting each, check line 57 reads the number you expect** — that is the whole
check, and it takes two seconds.

---

## The same six clicks every time

1. kaggle.com → **Create** → **New Notebook**
2. **File → Editor Type → Script.** These are scripts, not cell notebooks. If you
   skip this the paste still runs, but the layout will not match what you see here.
3. Select the placeholder code, delete it, paste the whole of `run.py`.
4. Right sidebar → **Input** → **+ Add Input** → attach what that step lists below
   (tabs across the top: Competitions / Datasets / Notebooks).
5. Right sidebar → **Session options** → set **Accelerator** and **Internet** as
   listed. These differ between steps — notebook 6 is the odd one out on both.
6. Top right → **Save Version** → **Save & Run All (Commit)** → Save.

Then close the tab. It runs server-side; you do not need to stay on the page.

---

## 1. `00_dicom_header_scan` — CPU, ~1 h

| setting | value |
|---|---|
| Input | the competition `rsna-knee-abnormality-detection` |
| Accelerator | **None** |
| Internet | **Off** |

**When it finishes**, open the notebook → **Output** tab → download
`series_headers.parquet`.

Then: kaggle.com → **Create** → **New Dataset** → upload that one file → title it
exactly **`knee-phase1-artifacts`**. The URL must end up as
`kaggle.com/datasets/martijnlustig/knee-phase1-artifacts` — steps 2–5 mount it by
that exact name and will not find it under any other.

## 2–5. `03_cache_build_shard0`, `shard1`, `shard2`, `shard3` — CPU

Four separate notebooks, same settings. This is the slow part; start them and
leave them.

| setting | value |
|---|---|
| Input | the competition **+** your `martijnlustig/knee-phase1-artifacts` |
| Accelerator | **None** |
| Internet | **Off** |

Kaggle caps how many sessions run at once, so if the fourth refuses to start,
just run it when one of the others finishes. Order does not matter.

## 6. `97_train_v1pubfull_r50` — **GPU, ~3.5 h. The actual experiment.**

| setting | value |
|---|---|
| Input | the competition **+** `achelijndiamantidis/knee-phase1-public` **+** your four `knee-cache-build-*` **notebooks** (Notebooks tab, not Datasets) |
| Accelerator | **GPU T4 x2** |
| Internet | **On** — this one genuinely needs it, to fetch the pretrained resnet50 weights. Every other step stays off. |

If `achelijndiamantidis/knee-phase1-public` is not visible to you, ask us to make
it public. It repackages `dreaddevelopment/rsna-knee-labels` (CC0-1.0, already
public upstream), so it is safe to share — unlike the caches.

---

## When notebook 6 finishes

1. Open it → **Settings** → make it **Public**.
2. Send back the slug: `martijnlustig/knee-train-v1pubfull-r50`.

We mount it as a sixth blend member and measure. **You do not submit anything to
the competition** — we have five submissions a day and are using none of them.

## What this is for

Our blend uses five same-seed members. A sixth (resnet50) moved the board
0.938 → 0.940 — but our reseed floor is ±0.003, so that +0.002 is either a real
member effect or a lucky draw, and those point opposite ways. If it is real,
adding members is the best move we have; if it is draw, we should not spend hours
there at all.

**This trains the identical model with `RUN_SEED = 11` instead of 3.** That one
change is the entire experiment.

## Two things not to do

- **Do not paste your Kaggle API token into any chat**, ours or an AI's. Nothing
  above needs it — the web UI is enough. If you already pasted one anywhere,
  expire it: Settings → API → **Expire API Token**, then create a new one.
- **Do not set the seed to 3.** That is what the existing member used. The blend
  has a weight-fingerprint guard that refuses to run when two members are
  identical, so it would burn the full 3.5 h and produce nothing.
