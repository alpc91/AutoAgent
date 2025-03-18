def solve_for_k():
    # Given (3^k)^6 = 3^6
    # Simplify to 3^(6k) = 3^6 => 6k = 6 => k = 1
    left = (3**1)**6
    right = 3**6
    assert left == right, 'Solution does not match'
    return 1

if __name__ == '__main__':
    print(f'The value of k is: {{solve_for_k()}}')