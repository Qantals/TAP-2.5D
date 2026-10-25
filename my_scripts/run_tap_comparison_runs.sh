#!/usr/bin/env bash
# Run the TAP-2.5D annealer N times on its own APU case and convert the results
# into perflp eval configs.
#
# Why: the perflp paper's TAP-2.5D reference point is a single run (archived on
# the lab server as `output/decay_1-0.01`). A sweep check showed evaluated
# layouts up to 2 cycles / 9 W better than it on the plotted axes, so repeats are
# needed to see whether that one sample is typical. `sim_annealing.py` used to be
# unseeded and to write `output.txt` only after the last temperature level; both
# are fixed here (see my_scripts/README.md), so repeats are reproducible and an
# interrupted run keeps its best placement.
#
# The case config is this repository's own `configs/sys_apu.cfg` (CPU 12x12
# @274 W, GPU 18.2x18.2 @467 W, four HBM @10 W, links CPU-GPU, CPU-M0, CPU-M1,
# GPU-M2, GPU-M3 at 128 Gbps, 50 mm interposer, 1 mm granularity, `adpTWv2`
# cost, decay 0.95, T 1.0 -> 0.01, 4500 steps).
#
# HotSpot runs inside the annealer loop, so the runs are strictly serial: never
# start two of them, or one of perflp's own runs, at the same time.
#
# Usage (from this repository's root):
#   bash my_scripts/run_tap_comparison_runs.sh --dry-run
#   bash my_scripts/run_tap_comparison_runs.sh                 # 5 x ~21 min
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TAP_ROOT="$(dirname "$SCRIPT_DIR")"
PERFLP_ROOT="$(dirname "$TAP_ROOT")"
cd "$TAP_ROOT"

TAP_CFG="configs/sys_apu.cfg"
RUNS=5
FIRST_SEED=42
DRY_RUN=0
TEMPLATE="$PERFLP_ROOT/config/eval/tap_four_mem_c45lat_d8.yaml"
EVAL_DIR="$PERFLP_ROOT/config/eval"
REPORT_ROOT="report/tap_runs"
OUT_ROOT="output/runs"

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        --runs) RUNS="$2"; shift ;;
        --first-seed) FIRST_SEED="$2"; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done

for k in $(seq 1 "$RUNS"); do
    seed=$((FIRST_SEED + k - 1))
    out_dir="$OUT_ROOT/run$k"
    eval_cfg="$EVAL_DIR/tap_run${k}_four_mem_c45lat_d8.yaml"
    echo "run $k (seed $seed):"
    echo "  anneals  sim_annealing.py -c $TAP_CFG -d $out_dir/ -g seed=$seed"
    echo "  converts $out_dir/output.txt -> $eval_cfg"
    if [ "$DRY_RUN" = "1" ]; then
        continue
    fi
    mkdir -p "$out_dir"
    conda run -n tap2.5d python -u sim_annealing.py \
        -c "$TAP_CFG" -d "$out_dir/" -g "seed=$seed" > "$out_dir/run.log" 2>&1
    conda run -n tap2.5d python3 my_scripts/tap_layout_to_config.py \
        --template "$TEMPLATE" --out "$eval_cfg" \
        --report-path "$REPORT_ROOT/run$k" "$out_dir/output.txt"
done

if [ "$DRY_RUN" = "1" ]; then
    echo "(dry run: nothing was written or executed)"
else
    echo "done: $RUNS runs; evaluate each on the perflp side with"
    echo "  conda run -n perflp python -m perflp eval-surrogate -c $EVAL_DIR/tap_run<k>_four_mem_c45lat_d8.yaml"
fi
