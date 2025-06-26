import numpy as np
from EFieldFJW.celxx import cel_x
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
    rho = rho / radius
    zeta = zeta / radius

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

    fzeta = cel_x(kk, rr) * A_3_2 * (zeta / denominator) * kqr2

    # doing the integral for frho
    #   I1
    rr = rr * rho
    frho_1 = cel_x(kk, rr)
            # * (A_3_2 / rho) * (rho / denominator)
    #   I2
    #       - because this cannot be put in an elliptical integral,
    #         just do the integration normally.
    # Define symbolic variables
    def integrand(theta, A, rho):
        denominator = (A - 2 * rho * np.cos(theta)) ** (3 / 2)
        return np.cos(theta) / denominator

    # Perform the integration from 0 to pi
    frho_2, error = quad(integrand, 1e-8, np.pi, args=(A, rho))

    frho = (frho_1 - frho_2) * (A_3_2 / denominator) * kqr2

    return fzeta, frho