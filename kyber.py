import numpy as np
from numpy.polynomial import Polynomial

# Constants
Q = 17          # Modulo for coefficients
N = 4           # Modulo x^N + 1 for all the polynomials to keep the polynomial degree bounded


p = Polynomial([2, 4, 1, 5, 10, 3, 69])

def modulo(poly):
    """apply the modulos for coefficients and degrees to the given polynomial"""

    print(poly)

    res = [0 for _ in range(N)]

    for i in range(len(poly.coef)):
        if np.floor(i / N) % 2 == 0:
            res[i % N] += poly.coef[i] % Q
        else:
            res[i % N] -= poly.coef[i] % Q

    return Polynomial(res)


print(modulo(p))

