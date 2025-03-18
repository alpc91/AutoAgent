import sympy as sp

k = sp.symbols('k')
equation = (3**k)**6 - 3**6
solution = sp.solve(equation, k)
print(f'Solution: k = {solution[0]}')