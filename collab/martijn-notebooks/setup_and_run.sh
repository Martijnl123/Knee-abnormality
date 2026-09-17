#!/usr/bin/env bash
# Run the whole chain from your own machine, with your own token.
#
#   1. Join the competition first (see README step 0) -- nothing works before that.
#   2. export KAGGLE_API_TOKEN=...   <- in YOUR shell. Never in a chat, never in a
#                                       file you send anyone, never in an AI prompt.
#   3. bash setup_and_run.sh
#
# This pushes the CPU stages, waits for them, and stops before the GPU stage so
# you can confirm the cache looks right before spending 3.5 h of quota.
set -euo pipefail

: "${KAGGLE_API_TOKEN:?set KAGGLE_API_TOKEN in your shell first}"
ME="${KAGGLE_PUSH_ACCOUNT:?set KAGGLE_PUSH_ACCOUNT to your kaggle username}"

export KAGGLE_DEPENDS_ACCOUNT="$ME"
export KAGGLE_ARTIFACTS_DATASET="$ME/knee-phase1-artifacts"
export KAGGLE_PUBLIC_DATASET="achelijndiamantidis/knee-phase1-public"

wait_for () {                     # $1 = owner/slug
  echo "waiting on $1"
  while true; do
    s="$(kaggle kernels status "$1" 2>&1 | tail -1)"
    case "$s" in
      *COMPLETE*) echo "  done: $1"; return 0 ;;
      *ERROR*|*CANCEL*) echo "  FAILED: $s"; return 1 ;;
      *) sleep 60 ;;
    esac
  done
}

echo "== 1/3  header scan (CPU, ~1 h) =="
kaggle kernels push -p 00_dicom_header_scan
wait_for "$ME/knee-dicom-header-scan-cpu-headers-only"

echo "== 2/3  publish series_headers.parquet as your artifacts dataset =="
rm -rf _scan && mkdir -p _scan
kaggle kernels output "$ME/knee-dicom-header-scan-cpu-headers-only" -p _scan
test -f _scan/series_headers.parquet || {
  echo "series_headers.parquet missing from the scan output"; exit 1; }
cat > _scan/dataset-metadata.json <<JSON
{"title": "knee-phase1-artifacts", "id": "$ME/knee-phase1-artifacts",
 "licenses": [{"name": "unknown"}]}
JSON
rm -f _scan/*.log
kaggle datasets create -p _scan -q || kaggle datasets version -p _scan -m "update" -q
echo "  published $ME/knee-phase1-artifacts"

echo "== 3/3  four cache shards (CPU) =="
for s in 0 1 2 3; do kaggle kernels push -p "03_cache_build_shard$s"; done
for s in 0 1 2 3; do wait_for "$ME/knee-cache-build-$s"; done

cat <<TXT

CPU stages done. The GPU stage is deliberately NOT started automatically -- it
costs ~3.5 h of your weekly 30, so look at a cache log first and confirm it
processed the studies it should have. When you are happy:

    kaggle kernels push -p 97_train_v1pubfull_r50

That one has RUN_SEED = 11 already set. Do not change it to 3.
When it finishes, make it public and send back:  $ME/knee-train-v1pubfull-r50
TXT
