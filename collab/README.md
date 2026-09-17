# `collab/` — handover folders for people outside this account

Each subfolder is a **generated** set of Kaggle kernels wired to a collaborator's
account, so they can run this pipeline on their own GPU without a credential ever
changing hands.

**These are build outputs, not sources.** Do not hand-edit them. They are produced
from `src/pipeline.py` with the account and dataset overrides set:

```bash
KAGGLE_PUSH_ACCOUNT=<their-name> \
KAGGLE_DEPENDS_ACCOUNT=<their-name> \
KAGGLE_ARTIFACTS_DATASET=<their-name>/knee-phase1-artifacts \
KAGGLE_PUBLIC_DATASET=achelijndiamantidis/knee-phase1-public \
python eda/generate_kernels.py --write
```

then the relevant `kaggle/<dir>/` folders are copied here. The three account names
answer three different questions — who pushes, who owns the datasets, whose kernel
outputs get mounted — and E118 records why collapsing any pair breaks one of the
two cases.

**They go stale.** If `src/pipeline.py` changes, regenerate rather than patching.
The `kaggle/` tree is the one the drift check enforces; nothing checks these.

**Why the repo is safe to share.** `eda/preflight.sh` enforces that no
patient-derived file is tracked, and nothing here carries competition data — only
code. The competition-derived assets (`knee-cache-build-*`,
`knee-phase1-artifacts`) live on Kaggle and stay team-only.
