x = [42.0, 12.0, 31.0, 27.0, 43.0, 42.0]
y = [8.0, 38.0, 19.0, 8.0, 22.0, 40.0]
width = [12.0, 18.2, 11.87, 11.87, 7.75, 7.75]
height = [12.0, 18.2, 7.75, 7.75, 11.87, 11.87]

def mm2m():
    for i in range(len(x)):
        width[i] = width[i] * 1e-3
        height[i] = height[i] * 1e-3
        x[i] = x[i] * 1e-3 - width[i] / 2
        y[i] = y[i] * 1e-3 - height[i] / 2
    print(f"    x: {x}")
    print(f"    y: {y}")
    print(f"    width: {width}")
    print(f"    height: {height}")

def m2mm():
    return
    x= [0.019, 0.0159, 0.01115, 0.0311, 0.00805, 0.03421]
    y= [0.0282, 0.0099, 0.028265, 0.028265, 0.013065, 0.013065]
    width= [0.012, 0.0182, 0.00775, 0.00775, 0.00775, 0.00775]
    height= [0.012, 0.0182, 0.01187, 0.01187, 0.01187, 0.01187]
    for i in range(6):
        width[i] = width[i] * 1e3
        height[i] = height[i] * 1e3
        x[i] = x[i] * 1e3 + width[i] / 2
        y[i] = y[i] * 1e3 + height[i] / 2
        # x[i] = x[i] * 1e3
        # y[i] = y[i] * 1e3
    print(f"\"x\": {x},")
    print(f"\"y\": {y},")
    print(f"\"width\": {width},")
    print(f"\"height\": {height},")

    print("x = " + ", ".join(f"{v:.3f}" for v in x))
    print("y = " + ", ".join(f"{v:.3f}" for v in y))
    print("width = " + ", ".join(f"{v:.3f}" for v in width))
    print("height = " + ", ".join(f"{v:.3f}" for v in height))

if __name__ == "__main__":
    mm2m()
    # m2mm()
