import math

# Solve for k in the equation (3^k)^6 = 3^6
# Simplify the equation to find k

# Given equation components
left_side_base = 3
right_side_exponent = 6

# Since (a^b)^c = a^(b*c), we can simplify the left side of the equation
def find_k():
    # The exponents on both sides must be equal, so set them equal to each other and solve for k
    # k * 6 = right_side_exponent
    k = right_side_exponent / 6
    return k

# Calculate the value of k
k_value = find_k()
print(f'The value of k is: {k_value}')
