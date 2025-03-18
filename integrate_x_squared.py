import scipy.integrate as spi

result, error = spi.quad(lambda x: x**2, 0, 5)
print(f"The integral of x^2 from 0 to 5 is: {result}")