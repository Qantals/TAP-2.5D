import random, os, math
import csv
import numpy as np
import config
import block_occupation
import routing
from copy import deepcopy
import time


def boundary_check(system, x, y, w, h):
    # w and h here includes microbump overhead
    guard = system.guard_gap
    if (x - w / 2) < guard:
        return False
    if (x + w / 2) > system.intp_size - guard:
        return False
    if (y - h / 2) < guard:
        return False
    if (y + h / 2) > system.intp_size - guard:
        return False
    return True


def close_neighbor(system, grid):
    """slightly moving chiplets, do not consider rotation"""
    chiplet_order = np.random.permutation(range(system.chiplet_count))
    granularity = system.granularity
    for p in chiplet_order:
        direction_order = np.random.permutation(["up", "down", "left", "right"])
        xx, yy, width, height = (
            system.x[p],
            system.y[p],
            system.width[p] + 2 * system.hubump[p],
            system.height[p] + 2 * system.hubump[p],
        )
        # print ('chiplet ', p + 2)
        for d in direction_order:
            # print (d)
            # re-connect the direction with the appropriate function in order to easily visulize using print-grid(). The dirctions are referring to the grid printed on screen, the directions in functions are referring to conventional x-y coordinates, origin in the left-bottom corner.
            if d == "left":
                new_y = yy - granularity
                if block_occupation.check_down_occupation(
                    grid, granularity, xx, new_y, width, height
                ) and boundary_check(system, xx, new_y, width, height):
                    # print ('chiplet', p + 2, d)
                    return p, xx, new_y
            elif d == "right":
                new_y = yy + granularity
                if block_occupation.check_up_occupation(
                    grid, granularity, xx, new_y, width, height
                ) and boundary_check(system, xx, new_y, width, height):
                    # print ('chiplet', p + 2, d)
                    return p, xx, new_y
            elif d == "up":
                new_x = xx - granularity
                if block_occupation.check_left_occupation(
                    grid, granularity, new_x, yy, width, height
                ) and boundary_check(system, new_x, yy, width, height):
                    # print ('chiplet', p + 2, d)
                    return p, new_x, yy
            elif d == "down":
                new_x = xx + granularity
                if block_occupation.check_right_occupation(
                    grid, granularity, new_x, yy, width, height
                ) and boundary_check(system, new_x, yy, width, height):
                    # print ('chiplet', p + 2, d)
                    return p, new_x, yy
    print("No chiplet can be moved.")
    exit()


def jumping_neighbor(system, grid):
    """define a neighbor placement as move one chiplet to anywhere can be located.
    rotate if needed. We do not consider swapping, since can't gaurantee the placement
    is still legal (no overlap) after swapping"""

    n = system.chiplet_count
    granularity = system.granularity
    count = 0
    while True:
        pick_chiplet = random.randint(0, n - 1)
        x_new = random.randint(1, system.intp_size / granularity - 1) * granularity
        y_new = random.randint(1, system.intp_size / granularity - 1) * granularity
        rotation = random.randint(0, 1)
        if rotation == 1:
            chiplet_width, chiplet_height = (
                system.height[pick_chiplet],
                system.width[pick_chiplet],
            )
        else:
            chiplet_height, chiplet_width = (
                system.height[pick_chiplet],
                system.width[pick_chiplet],
            )
        if boundary_check(
            system,
            x_new,
            y_new,
            chiplet_width + 2 * system.hubump[pick_chiplet],
            chiplet_height + 2 * system.hubump[pick_chiplet],
        ) and block_occupation.replace_block_occupation(
            grid,
            granularity,
            x_new,
            y_new,
            chiplet_width + 2 * system.hubump[pick_chiplet],
            chiplet_height + 2 * system.hubump[pick_chiplet],
            pick_chiplet,
        ):
            print("found a random placement at", count, "th trial")
            break
        count += 1
        if count > 10000:
            # it's not easy to find a legal placement using random method. try move each chiplet (in random order) slightly until find a legal solution
            print("cannot find a legal random placement, go with close_neighbor")
            return close_neighbor(system, grid)
    return pick_chiplet, x_new, y_new, rotation


def accept_probability(old_temp, new_temp, old_length, new_length, T, weight):
    if weight == "equal":
        a, b = 0.5, 0.5
    elif weight == "adpT":
        a = 0.1 + (max(old_temp, new_temp) - 45) * 0.01
        b = 0.5
    elif weight == "adpTW":
        a = min(0.1 + (max(old_temp, new_temp) - 45) * 0.01, 0.9)
        b = 1 - a
    elif weight == "adpTWv2":
        if old_temp < 85 and new_temp < 85:
            a = 0
        else:
            a = min(0.1 + (max(old_temp, new_temp) - 45) * 0.01, 0.9)
        b = 1 - a
    elif "custom" in weight:
        splitted = weight.split("-")
        if len(splitted) != 3:
            raise ValueError("Invalid weight option!")
        a = float(splitted[1])
        b = float(splitted[2])
    else:
        raise ValueError("Invalid weight option!")
    if temp_min != temp_max and length_min != length_max:
        old_cost = a * (old_temp - temp_min) / (temp_max - temp_min) + b * (
            old_length - length_min
        ) / (length_max - length_min)
        new_cost = a * (new_temp - temp_min) / (temp_max - temp_min) + b * (
            new_length - length_min
        ) / (length_max - length_min)
    else:
        old_cost = a * (old_temp - temp_min) + b * (old_length - length_min)
        new_cost = a * (new_temp - temp_min) + b * (new_length - length_min)
    delta = -(new_cost - old_cost)
    if "up" in weight:
        delta = -delta
    if delta > 0:
        ap = 1
    else:
        ap = math.exp(delta / T)
    # print (old_temp, new_temp, old_length, new_length, T, delta, ap)
    return ap, old_cost, new_cost


# def accept_probability(old_temp, new_temp, T):
# 	delta = (old_temp - new_temp)
# 	# print (old_temp, new_temp, T, delta)
# 	if delta > 0:
# 		ap = 1
# 	else:
# 		ap = math.exp( delta / T )
# 	return ap


def update_minmax(temp, length):
    global temp_max, temp_min, length_max, length_min
    if temp > temp_max:
        temp_max = temp
    if temp < temp_min:
        temp_min = temp
    if length > length_max:
        length_max = length
    if length < length_min:
        length_min = length


def register_log(
    system_best, step_best, temp_best, length_best, T, step, old_cost, new_cost
):
    with open(system_best.path + "log.txt", "a+") as LOG:
        LOG.write("*" * 15 + "\n")
        LOG.write(f"Weight: {system_best.weight}\n")
        LOG.write("T = " + str(T) + "\t step = " + str(step) + "\n")
        LOG.write("old_cost = " + str(old_cost) + "\n")
        LOG.write("new_cost = " + str(new_cost) + "\n")
        LOG.write("delta = old - new = " + str(old_cost - new_cost) + "\n")
        LOG.write(
            "step_best = "
            + str(step_best)
            + "\n"
            + "temp_best = "
            + str(temp_best)
            + "\n"
            + "length_best = "
            + str(length_best)
            + "\n"
        )
        LOG.write(
            "x = " + str(system_best.x) + "\n" + "y = " + str(system_best.y) + "\n"
        )
        LOG.write(
            "width = "
            + str(system_best.width)
            + "\n"
            + "height = "
            + str(system_best.height)
            + "\n"
        )


def register_step(system, step, temp, length, T, old_cost, new_cost):
    with open(system.path + "step.txt", "a+") as LOG:
        LOG.write("*" * 15 + "\n")
        LOG.write("T = " + str(T) + "\t step = " + str(step) + "\n")
        LOG.write("temp = " + str(temp) + "\n" + "length = " + str(length) + "\n")
        LOG.write("old_cost = " + str(old_cost) + "\n")
        LOG.write("new_cost = " + str(new_cost) + "\n")
        LOG.write("delta = old - new = " + str(old_cost - new_cost) + "\n")
        LOG.write("x = " + str(system.x) + "\n" + "y = " + str(system.y) + "\n")
        LOG.write(
            "width = "
            + str(system.width)
            + "\n"
            + "height = "
            + str(system.height)
            + "\n"
        )


def anneal():
    # first step: read config and generate initial placement
    global temp_max, temp_min, length_max, length_min
    temp_max, temp_min, length_max, length_min = 0, 200, 0, 200
    system = config.read_config()
    print(f"Weight: {system.weight}")
    system_new = deepcopy(system)
    system_best = deepcopy(system)
    step = 1
    step_best = 1

    # --- timing setup ---
    timing_path = system.path + "timing.csv"
    _cumul_time = 0.0

    _t_step0 = time.perf_counter()
    system.gen_flp("step_" + str(step))
    system.gen_ptrace("step_" + str(step))
    _t0 = time.perf_counter()
    temp_current = system.run_hotspot("step_" + str(step))
    _t1 = time.perf_counter()
    _t_hotspot_initial = _t1 - _t0
    system.clean_hotspot("step_" + str(step))
    # TODO: no routing
    if False:
        length_current = 0.0
        _t_routing_initial = 0.0
    else:
        _t0 = time.perf_counter()
        length_current = routing.solve_Cplex(system)
        _t1 = time.perf_counter()
        _t_routing_initial = _t1 - _t0
    _t_step_wall_initial = time.perf_counter() - _t_step0
    _t_others_initial = _t_step_wall_initial - _t_hotspot_initial - _t_routing_initial
    _cumul_time += _t_step_wall_initial

    temp_best, length_best = temp_current, length_current
    update_minmax(temp_current, length_current)
    print("step_" + str(step), "temp =", temp_current, "length =", length_current)
    x_best, y_best = system.x[:], system.y[:]
    intp_size = system.intp_size
    granularity = system.granularity
    grid = block_occupation.initialize_grid(
        int(intp_size / granularity), system.guard_gap, granularity
    )
    for i in range(system.chiplet_count):
        grid = block_occupation.set_block_occupation(
            grid,
            granularity,
            system.x[i],
            system.y[i],
            system.width[i] + 2 * system.hubump[i],
            system.height[i] + 2 * system.hubump[i],
            i,
        )
    # block_occupation.print_grid(grid)

    # set annealing parameters
    T = 1.0
    T_min = 0.01
    alpha = system.decay
    # jumping_ratio = T_min / alpha
    jumping_ratio = 0.9  # fixed to 10% chance to jump

    # write initial step timing to CSV
    with open(timing_path, "w") as f:
        f.write(
            "step,temperature,t_hotspot,t_routing,t_others,t_step_total,t_cumulative\n"
        )
        f.write(
            f"{step},{T:.6f},{_t_hotspot_initial:.6f},{_t_routing_initial:.6f},{_t_others_initial:.6f},{_t_step_wall_initial:.6f},{_cumul_time:.6f}\n"
        )

    # start simulated annealing
    old_cost, new_cost = 0, 0
    register_log(
        system_best, step_best, temp_best, length_best, T, step, old_cost, new_cost
    )
    register_step(system, step, temp_current, length_current, T, old_cost, new_cost)
    while T > T_min:
        i = 1
        while i <= intp_size:
            step += 1
            _t_step0 = time.perf_counter()
            print("*" * 15)
            print("step_" + str(step), " T = ", T, " i = ", i)
            jump_or_close = random.random()
            if 1 - jumping_ratio > jump_or_close:
                chiplet_moving, x_new, y_new, rotation = jumping_neighbor(system, grid)
            else:
                chiplet_moving, x_new, y_new = close_neighbor(system, grid)
                rotation = 0
            print(
                "moving chiplet",
                chiplet_moving + 2,
                "from (",
                system.x[chiplet_moving],
                system.y[chiplet_moving],
                ") to (",
                x_new,
                y_new,
                "), rotation = ",
                rotation,
            )
            system_new = deepcopy(system)
            system_new.x[chiplet_moving], system_new.y[chiplet_moving] = x_new, y_new
            if rotation == 1:
                system_new.rotate(chiplet_moving)
                # system_new.height[chiplet_moving], system_new.width[chiplet_moving] = system_new.width[chiplet_moving], system_new.height[chiplet_moving]
            system_new.gen_flp("step_" + str(step))
            system_new.gen_ptrace("step_" + str(step))
            _t0 = time.perf_counter()
            temp_new = system_new.run_hotspot("step_" + str(step))
            _t1 = time.perf_counter()
            _t_hotspot = _t1 - _t0
            system_new.clean_hotspot("step_" + str(step))
            # TODO: no routing
            if False:
                length_new = 0.0
                _t_routing = 0.0
            else:
                _t0 = time.perf_counter()
                length_new = routing.solve_Cplex(system_new)
                _t1 = time.perf_counter()
                _t_routing = _t1 - _t0
            _t_step1 = time.perf_counter()
            _t_step_wall = _t_step1 - _t_step0
            _t_others = _t_step_wall - _t_hotspot - _t_routing
            _cumul_time += _t_step_wall
            with open(timing_path, "a") as f:
                f.write(
                    f"{step},{T:.6f},{_t_hotspot:.6f},{_t_routing:.6f},{_t_others:.6f},{_t_step_wall:.6f},{_cumul_time:.6f}\n"
                )
            print("Temp =", temp_new, "Length =", length_new)
            update_minmax(temp_new, length_new)
            # ap = accept_probability(temp_current, temp_new, T)
            ap, old_cost, new_cost = accept_probability(
                temp_current, temp_new, length_current, length_new, T, system.weight
            )
            register_step(system_new, step, temp_new, length_new, T, old_cost, new_cost)
            r = random.random()
            if ap > r:
                # clear last step's occupation of chiplet_moving (system)
                grid = block_occupation.clear_block_occupation(
                    grid,
                    granularity,
                    system.x[chiplet_moving],
                    system.y[chiplet_moving],
                    system.width[chiplet_moving] + 2 * system.hubump[chiplet_moving],
                    system.height[chiplet_moving] + 2 * system.hubump[chiplet_moving],
                    chiplet_moving,
                )
                # set new occupation with rotation (system_new)
                grid = block_occupation.set_block_occupation(
                    grid,
                    granularity,
                    x_new,
                    y_new,
                    system_new.width[chiplet_moving]
                    + 2 * system.hubump[chiplet_moving],
                    system_new.height[chiplet_moving]
                    + 2 * system.hubump[chiplet_moving],
                    chiplet_moving,
                )
                # update system
                system = deepcopy(system_new)
                temp_current = temp_new
                length_current = length_new
                bap, _, _ = accept_probability(
                    temp_best,
                    temp_current,
                    length_best,
                    length_current,
                    T,
                    system.weight,
                )
                if bap >= 1:
                    # if temp_new < temp_best:
                    temp_best = temp_new
                    length_best = length_new
                    system_best = deepcopy(system_new)
                    step_best = step
                print("AP = ", ap, " > ", r, " Accept!")
                # block_occupation.print_grid(grid)
            else:
                print("AP = ", ap, " < ", r, " Reject!")
            i += 1
        register_log(
            system_best, step_best, temp_best, length_best, T, step, old_cost, new_cost
        )
        T *= alpha
        # jumping_ratio /= alpha
    # os.system('rm ' + system.path + '{*.flp,*.lcf,*.ptrace,*.steady}')
    print(
        f"Total runtime: {_cumul_time:.3f}s across {step} steps, "
        f"avg {_cumul_time / max(step, 1):.4f}s/step"
    )
    os.system("rm " + system.path + "*.flp")
    os.system("rm " + system.path + "*.lcf")
    os.system("rm " + system.path + "*.ptrace")
    os.system("rm " + system.path + "*.steady")
    os.system("rm " + system.path + "*.png")
    # os.system('gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile='+system.path+'combine.pdf '+system.path + 'step_{1..'+str(step_best)+'}L4.pdf')
    os.system("rm " + system.path + "step_*.pdf")
    return system_best, step_best, temp_best, length_best


if __name__ == "__main__":
    solution, step_best, temp_best, length_best = anneal()
    print("final solution:")
    print(f"step_best = {step_best}")
    print(f"temp_best = {temp_best}")
    print(f"length_best = {length_best}")
    print(f"x = {solution.x}")
    print(f"y = {solution.y}")
    print(f"width = {solution.width}")
    print(f"height = {solution.height}")
    with open(solution.path + "output.txt", "w") as OUTPUT:
        OUTPUT.write(
            "step_best = "
            + str(step_best)
            + "\n"
            + "temp_best = "
            + str(temp_best)
            + "\n"
            + "length_best = "
            + str(length_best)
            + "\n"
        )
        OUTPUT.write("x = " + str(solution.x) + "\n" + "y = " + str(solution.y) + "\n")
        OUTPUT.write(
            "width = "
            + str(solution.width)
            + "\n"
            + "height = "
            + str(solution.height)
            + "\n"
        )
