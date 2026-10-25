# my_scripts

Additions to the TAP-2.5D checkout that belong to the perflp comparison, kept
here rather than in the perflp repository. The upstream code is untouched apart
from the two fixes described below.

## Fixes to the annealer (2026-10-03)

`sim_annealing.py`, `config.py`, `system.py`:

1. **`-g seed=<int>`** — the annealer used `random` / `numpy.random` without
   seeding, so every run drew a different trajectory and none was reproducible.
   `config.py` parses `seed` from `-g` into `system.set_seed(...)`, and
   `sim_annealing.py` seeds both RNGs in `seed_from_argv()` **before**
   `config.read_config()`, because the B\*-tree initial placement is drawn
   inside `read_config()` (seeding later would leave the starting point
   unreproducible). Without the option the printed header says
   `Random seed: unset (this run is not reproducible)`, i.e. the old behaviour.
   Checked: two runs with `-g seed=7` give the same initial placement, `-g seed=8`
   a different one.

2. **Incremental result recording** — `output.txt` was written once, after the
   last of ~4500 steps, so any run that died earlier (HotSpot failure, OOM, lost
   session, wall-clock limit) lost the whole search even though the best
   placement was already known; the cleanup also removed the intermediate
   artifacts. `register_log()` now calls the new `write_output()` for the initial
   placement and after **every temperature level**, so `output.txt` is never more
   than one level (50 steps) stale, and it carries `seed` and an `updated`
   timestamp. Checked by killing a run after ~60 steps: `output.txt` was present
   with the best-so-far placement.

`log.txt` (per-level best) and `step.txt` (every evaluated candidate) are
unchanged; `timing.csv` still holds the per-step HotSpot / routing split.

## `tap_layout_to_config.py`

TAP reports placements in `output.txt` with `x`/`y` as chiplet **centres** in mm
and a per-chiplet `width`/`height` that may be rotated; perflp configs want the
**lower-left corner** in metres, in the order CPU, GPU, memory chiplets (the
order TAP uses as well). The script prints the perflp `floorplan:` block or
writes a full eval config from a template:

```bash
python my_scripts/tap_layout_to_config.py output/runs/run1/output.txt
python my_scripts/tap_layout_to_config.py \
    --template ../config/eval/tap_four_mem_c45lat_d8.yaml \
    --out ../config/eval/tap_run1_four_mem_c45lat_d8.yaml \
    --report-path report/tap_runs/run1 output/runs/run1/output.txt
```

Verified both ways: the perflp paper's TAP-2.5D coordinates are exactly the
centres `x = [40, 13, 41, 40, 10, 14]`, `y = [25, 25, 14, 36, 39, 11]`, which the
script converts back to the config values bit for bit.

## `run_tap_comparison_runs.sh`

Runs the annealer N times (default 5, seeds 42..46) with this repository's own
`configs/sys_apu.cfg` — the four-memory APU case that matches the perflp
platform (CPU 12x12 @274 W, GPU 18.2x18.2 @467 W, four HBM @10 W, links
CPU-GPU, CPU-M0, CPU-M1, GPU-M2, GPU-M3 at 128 Gbps, 50 mm interposer, 1 mm
granularity, `adpTWv2` cost, decay 0.95, T 1.0 -> 0.01). Each run writes to
`output/runs/run<k>/` and is converted into
`../config/eval/tap_run<k>_four_mem_c45lat_d8.yaml`.

```bash
bash my_scripts/run_tap_comparison_runs.sh --dry-run   # plan only
bash my_scripts/run_tap_comparison_runs.sh             # 5 x ~21 min
```

**Serial:** HotSpot is called inside the annealer loop, so two runs of this
script, or one of these plus a perflp `simanneal` / `eval-surrogate`, must never
overlap. Use the `tap2.5d` conda environment (CPLEX for the routing MILP).

## Archived reference runs

The lab server (`ssh lab:/home/share/HDstorage/zyh/open_source/TAP-2.5D/output/`)
holds five repeats of this case from the unseeded code; `decay_1-0.01` is the
placement used as the perflp paper's TAP-2.5D point. They were copied into
`report/tap_runs/server_archive/` on the perflp side and converted with the same
script.
