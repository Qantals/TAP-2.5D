def print_grid(grid):
    for i in grid:
        print (i)
    print

def initialize_grid(mi, guard_gap=1.0, granularity=1.0):
    grid = [[0 for _ in range(mi+1)] for _ in range(mi+1)]
    # boundary protection + guard gap
    guard_cells = int(guard_gap / granularity)
    for i in range(mi+1):
        for g in range(guard_cells + 1):
            grid[g][i] = 1
            grid[mi-g][i] = 1
            grid[i][g] = 1
            grid[i][mi-g] = 1
    return grid

# width and height here are parameters passed in. We consider it is including microbump overhead. The addition should be handled before this module.
def check_block_occupation(grid, granularity, xx, yy, width, height):
    # print (int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1)
    for i in range(int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1):
        if (sum(grid[i][int(yy/granularity)-int(height/2/granularity+0.49):int(yy/granularity)+int(height/2/granularity+0.49)+1])):
            return False
    return True

def check_left_occupation(grid, granularity, xx, yy, width, height):
    i = int(xx/granularity) - int(width/2/granularity+0.49)
    if i<=0:
        return False
    if (sum(grid[i][int(yy/granularity)-int(height/2/granularity+0.49):int(yy/granularity)+int(height/2/granularity+0.49)+1])):
        # print (i, grid[i][int(yy/granularity)-int(height/2/granularity+0.49):int(yy/granularity)+int(height/2/granularity+0.49)+1])
        return False
    else:
        return True

def check_right_occupation(grid, granularity, xx, yy, width, height):
    i = int(xx/granularity) + int(width/2/granularity+0.49)
    intp_size = (len(grid) - 1) * granularity
    if i >= intp_size:
        return False
    if (sum(grid[i][int(yy/granularity)-int(height/2/granularity+0.49):int(yy/granularity)+int(height/2/granularity+0.49)+1])):
        # print (i, grid[i][int(yy/granularity)-int(height/2/granularity+0.49):int(yy/granularity)+int(height/2/granularity+0.49)+1])
        return False
    else:
        return True

def check_down_occupation(grid, granularity, xx, yy, width, height):
    j = int(yy/granularity) - int(height/2/granularity+0.49)
    if j<=0:
        return False
    for i in range(int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1):
        if grid[i][j]:
            # print (i,j, grid[i][j])
            return False
    return True

def check_up_occupation(grid, granularity, xx, yy, width, height):
    j = int(yy/granularity) + int(height/2/granularity+0.49)
    intp_size = (len(grid) - 1) * granularity
    if j >= intp_size:
        return False
    for i in range(int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1):
        if grid[i][j]:
            # print (i,j, grid[i][j])
            return False
    return True

def set_block_occupation(grid, granularity, xx, yy, width, height, chiplet_index):
    for i in range(int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1):
        for j in range(int(yy/granularity)-int(height/2/granularity+0.49), int(yy/granularity)+int(height/2/granularity+0.49)+1):
            grid[i][j] = chiplet_index + 2
    return grid

def clear_block_occupation(grid, granularity, xx, yy, width, height, chiplet_index):
    for i in range(int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1):
        for j in range(int(yy/granularity)-int(height/2/granularity+0.49), int(yy/granularity)+int(height/2/granularity+0.49)+1):
            if grid[i][j] != chiplet_index + 2:
                print (chiplet_index, grid[i][j], i, j)
                print ('x- ',int(xx/granularity)-int(width/2/granularity+0.49), int(xx/granularity)+int(width/2/granularity+0.49)+1, 'y-',int(yy/granularity)-int(height/2/granularity+0.49), int(yy/granularity)+int(height/2/granularity+0.49)+1)
                print ("something wrong, chiplet index mismatch")
                exit()
            grid[i][j] = 0
    return grid

def replace_block_occupation(grid, granularity, xx_new, yy_new, width, height, chiplet_index):
    for i in range(int(xx_new/granularity)-int(width/2/granularity+0.49), int(xx_new/granularity)+int(width/2/granularity+0.49)+1):
        for j in range(int(yy_new/granularity)-int(height/2/granularity+0.49), int(yy_new/granularity)+int(height/2/granularity+0.49)+1):
            if (grid[i][j] != chiplet_index + 2) and (grid[i][j] != 0):
                return False
    return True