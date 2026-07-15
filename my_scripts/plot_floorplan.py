#!/usr/bin/env python3
"""
Plot a floorplan from an output.txt file produced by sim_annealing.py.

Usage:
    python3 my_scripts/plot_floorplan.py output/custom-0.8-0.2/output.txt
"""

import argparse
import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def parse_output_txt(path):
    """Parse output.txt and return (x, y, width, height) lists."""
    with open(path) as f:
        content = f.read()

    def extract_list(name):
        m = re.search(rf"{name}\s*=\s*\[(.*?)\]", content)
        if not m:
            raise ValueError(f"Could not find '{name}' in {path}")
        return [float(v.strip()) for v in m.group(1).split(",")]

    x = extract_list("x")
    y = extract_list("y")
    width = extract_list("width")
    height = extract_list("height")
    return x, y, width, height


def plot_floorplan(x, y, width, height, output_path):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    # Determine plot bounds from the data
    all_xmin = [x[i] - width[i] / 2 for i in range(len(x))]
    all_xmax = [x[i] + width[i] / 2 for i in range(len(x))]
    all_ymin = [y[i] - height[i] / 2 for i in range(len(y))]
    all_ymax = [y[i] + height[i] / 2 for i in range(len(y))]

    margin = 2
    ax.set_xlim(min(all_xmin) - margin, max(all_xmax) + margin)
    ax.set_ylim(min(all_ymin) - margin, max(all_ymax) + margin)
    ax.set_aspect("equal")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Floorplan")

    # Colors for each chiplet
    colors = plt.cm.tab10.colors

    for i in range(len(x)):
        cx, cy = x[i], y[i]
        w, h = width[i], height[i]
        # Center → bottom-left corner
        rect = patches.Rectangle(
            (cx - w / 2, cy - h / 2),
            w, h,
            linewidth=2,
            edgecolor="black",
            facecolor=colors[i % len(colors)],
            alpha=0.6,
        )
        ax.add_patch(rect)
        # Label with chiplet index in the center
        ax.text(cx, cy, str(i), ha="center", va="center", fontsize=12, fontweight="bold")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Plot floorplan from output.txt")
    parser.add_argument("input", help="Path to output.txt")
    parser.add_argument("-o", "--output", default="my_scripts/output/floorplan.png", help="Output image path")
    args = parser.parse_args()

    x, y, width, height = parse_output_txt(args.input)
    print(f"Loaded {len(x)} chiplets from {args.input}")

    output_path = args.output

    plot_floorplan(x, y, width, height, output_path=output_path)


if __name__ == "__main__":
    main()
