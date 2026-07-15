#!/usr/bin/env python3

import subprocess
import sys
import os

usage = """
usage: split_grid_steady.py <grid_steady_file> <layers> <rows> <cols>

Takes a single grid_steady_file and splits it into layer-specific temperature files.

<grid_steady_file> -- path to the grid steady file (eg: example.grid.steady)
<layers>           -- no. of layers
<rows>             -- no. of rows in the grid
<cols>             -- no. of cols in the grid
"""

if len(sys.argv) != 5:
    print(usage)
    sys.exit(0)

grid_steady_file = sys.argv[1]
# grid_steady_prefix = grid_steady_file.split('.')[0]
grid_steady_prefix, ext = os.path.splitext(grid_steady_file)
if ".grid" in grid_steady_prefix:
    grid_steady_prefix, ext = os.path.splitext(grid_steady_prefix)
num_layers = int(sys.argv[2])
num_rows = int(sys.argv[3])
num_cols = int(sys.argv[4])

with open(grid_steady_file, "r") as ifp:
    for i in range(num_layers):
        # line = ifp.readline()[:-1]
        # layer_num = line.split()[1][:-1]
        layer_num = i
        if layer_num != 0:
            ifp.readline()

        split_file = f"{grid_steady_prefix}_layer{layer_num}.grid.steady"
        with open(split_file, "w") as ofp:
            for i in range(num_rows * num_cols):
                line = ifp.readline().split()
                ofp.write(f"{line[0]}    {round(float(line[1]), 2)}\n")
