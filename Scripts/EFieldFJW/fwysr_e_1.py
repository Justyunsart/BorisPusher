import numpy as np
from EFieldFJW.celxx import cel_x, cel
import settings.constants as c
from scipy.integrate import quad

"""
Testing a modified version of Bob_e based on elliptic integrals
"""

def feysr_e_1(rho, zeta, radius, q):
    """
    assumes cyl. space, and that the circle is at the XY plane centered at the origin

    Inputs:
    rho: float - the rho value of the field point
    zeta: float - the zeta value of the field point

    radius: float - the radius of the circle
    q: float - the charge of the circle
    """
    # make nums non-dimensional
    rho = abs(rho / radius)
    zeta = abs(zeta / radius)

    # --------------- #

    # determine constants outside cel stuff
    kqr2 = (c.coulomb * q) / (radius ** 2)
    _pp = rho * rho
    _zz = zeta * zeta

    A = _pp + _zz + 1 # value substituted in the process of cel
    A_3_2 = A ** 1.5
    denominator = A_3_2 * (radius ** 2)

    # --------------- #

    # doing the integral for fzeta
    B = 2 * rho  # value used as b in fzeta's decomposition
    kk =  (2 * B) / (A + B)
    rr = 2 / ((A - B) * np.sqrt(A + B))

    #fzeta = cel_x(kk, rr) * A_3_2 * (zeta / denominator) * kqr2
    k_c = np.sqrt(1 - kk)
    fzeta = cel(k_c, 1.0, 1.0, 1.0) * rr * A_3_2 * (zeta / denominator) * kqr2

    # doing the integral for frho
    #   I1
    rr = rr * rho
    #frho_1 = cel_x(kk, rr)
    #frho_1 = cel(k_c, 1, 1, 1) * rr
            # * (A_3_2 / rho) * (rho / denominator)
    #   I2
    #       - because this cannot be put in an elliptical integral,
    #         just do the integration normally.
    # Define symbolic variables
    def integrand(theta, A, rho):
        numerator = (1 - np.cos(theta)) / rho
        denominator = (1 - (2 * rho * np.cos(theta)) / A ) ** (3 / 2)
        #denominator = (A - 2 * rho * np.cos(theta)) ** (3 / 2)
        #return np.cos(theta) / denominator
        return numerator / denominator

    # Perform the integration from 0 to pi
    #frho_2, error = quad(integrand, 1e-8, np.pi, args=(A, rho))
    #frho_2, error = quad(integrand, 1e-8, np.pi, args=(A, rho), limit=200, epsabs=1e-10)

    #frho = (frho_2) * (rho / denominator) * kqr2

    Frho_c = (rho) / (A_3_2 * (radius ** 2))

    # Integration
    # Circle is broken into {resolution} slices; with each result being appended to the lists below.

    thetas = np.linspace(0, np.pi, 100,
                         dtype=np.float64)  # np.array of all the theta values used in the integration (of shape {resolution})
    cosines = np.cos(thetas)  # np.array of all the cosine values of the thetas
    denominators = (1 - ((2 * rho * cosines) / A)) ** (3 / 2)  # shared denominator values of fzeta and frho

    # replace zeros with a really small decimal.
    denominators[denominators == 0] = 1e-20

    frho = (1 - cosines / rho) / denominators

    # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
    frho = np.asarray(frho).sum() * Frho_c * kqr2

    return fzeta, frho

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    rhos = np.linspace(-2, 2, 100)
    frhos = np.empty(100)
    fzetas = np.empty(100)
    for i in range(100):
        fz, fr = feysr_e_1(rhos[i], 0.1, 1, 1e-11)
        frhos[i] = fr
        fzetas[i] = fz
    ax.plot(rhos, fzetas)

    plt.show()
