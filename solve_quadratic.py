import math

a = 1
b = -5
c = 6

discriminant = b**2 - 4*a*c

x1 = (-b + math.sqrt(discriminant)) / (2*a)
x2 = (-b - math.sqrt(discriminant)) / (2*a)

print(f"The solutions are x = {x1} and x = {x2}")