import scipy.integrate as spi

def integrand(x):
    return x**2

result, error = spi.quad(integrand, 0, 5)
print(f"Integral of x^2 from 0 to 5 is: {result}")