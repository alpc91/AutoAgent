# 解二次方程：x^2 + 3x - 4 = 0

import math

def solve_quadratic(a, b, c):
    # 计算判别式
    delta = b**2 - 4*a*c

    if delta >= 0:
        # 计算两个解
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        return x1, x2
    else:
        return None, None  # 如果判别式小于0，则无实数解

# 系数定义
a = 1
b = 3
c = -4

# 求解方程
solution = solve_quadratic(a, b, c)
if solution[0] is not None and solution[1] is not None:
    print("方程的解为：x1 =", solution[0], "和 x2 =", solution[1])
else:
    print("该方程没有实数解。")