#!/usr/bin/env python3
"""
Run sim_annealing.py across a range of weight values (custom-a-b, where a+b=1).

Usage:
    python3 run_experiments.py -c configs/sys_apu.cfg --step 0.1
    python3 run_experiments.py -c configs/sys_apu.cfg --start 0.0 --end 1.0 --step 0.25
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Run sim_annealing.py across weight values custom-a-b (a+b=1)."
    )
    parser.add_argument(
        "-c", "--config", default="configs/sys_apu.cfg",
        help="Path to the config file (default: configs/sys_apu.cfg)"
    )
    parser.add_argument(
        "--start", type=float, default=0.0,
        help="Starting value of 'a' (default: 0.0)"
    )
    parser.add_argument(
        "--end", type=float, default=1.0,
        help="Ending value of 'a' (default: 1.0)"
    )
    parser.add_argument(
        "--step", type=float, default=0.1,
        help="Step size for 'a' (default: 0.1)"
    )
    parser.add_argument(
        "--sim_script", default="sim_annealing.py",
        help="Path to the simulation script (default: sim_annealing.py)"
    )
    args = parser.parse_args()

    if args.step <= 0:
        print("Error: --step must be positive.", file=sys.stderr)
        sys.exit(1)

    # Generate a values from start to end inclusive, rounded to avoid float issues
    n_steps = round((args.end - args.start) / args.step)
    a_values = []
    for i in range(n_steps + 1):
        a = round(args.start + i * args.step, 3)
        if a > args.end + 1e-9:
            break
        a_values.append(a)

    print(f"Running {len(a_values)} experiments with a+b=1:")
    for a in a_values:
        b = round(1.0 - a, 3)
        print(f"  a={a}, b={b}")

    root_dir = os.path.dirname(os.path.abspath(__file__))

    for a in a_values:
        b = round(1.0 - a, 3)
        weight_label = f"custom-{a}-{b}"

        # Output directory for simulation results and log file
        data_dir = os.path.join(root_dir, "output", weight_label)
        log_file = os.path.join(data_dir, "print.log")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        cmd = [
            sys.executable, args.sim_script,
            "-c", args.config,
            "-d", data_dir + "/",
            "-g", f"weight={weight_label}",
        ]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] [{weight_label}] Running: {' '.join(cmd)}")
        print(f"[{timestamp}] [{weight_label}] Log: {log_file}")

        with open(log_file, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=root_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if result.returncode == 0:
            print(f"[{timestamp}] [{weight_label}] Finished successfully (exit code 0)")
        else:
            print(f"[{timestamp}] [{weight_label}] FAILED with exit code {result.returncode}")

    print("\nAll experiments completed.")


if __name__ == "__main__":
    main()
