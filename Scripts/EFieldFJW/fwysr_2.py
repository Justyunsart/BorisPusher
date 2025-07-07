
"""
e-field from a uniformly charged ring based on an ai solution,
created in elliptical integrals.
"""
import math
import numpy as np
from settings.constants import coulomb
from scipy.special import ellipk, ellipe

def fwysr_2(Q, radius, target_point):
    """
    Q: the total charge of the ring
    radius: the radius of the ring
    target_point: the point to evaluate the e-field at. assumed to be in cyl coordinates
    """
    # dimensionless

    # CONSTANTS
    #   save the target point as its base parts
    epsilon_0 = 8.854187817e-12  # Vacuum permittivity (F/m)
    t_rho = target_point[0] / radius
    #if math.isclose(1.0, t_rho, rel_tol = 1e-10 ,abs_tol=1e-2):
    #    print(t_rho)
    #    t_rho = 1.1
    t_theta = target_point[1]
    t_zeta = target_point[2] / radius
    #   q stuff
    qk = Q / (4 * np.pi**2 * epsilon_0)
    #   etc values that are used in the calculations, done here to avoid repeat
    a2 = 1
    p2 = t_rho ** 2
    z2 = t_zeta ** 2
    k2 = (4  * t_rho) / ((t_rho + 1) ** 2 + t_zeta ** 2)

    #----------#

    # INTEGRALS
    # cel arguments for sum of elliptical integrals:
    #   aK(m) + bE(m) = cel(sqrt(1-m^2), 1, a + b, a + b(1-m^2))
    # gather radial parameters for cel
    ddm = ((1 - t_rho) ** 2 + z2)
    sd = np.sqrt((t_rho + 1) ** 2 + t_zeta ** 2) # denominators of the scalars applied to the integrals
    #   scalars for the second and first kinds
    #_radial_e_scalar = (1 + p2 + z2) / ddm # 2nd
    #_radial_k_scalar = 1 # 1st
    #_radial_sum = _radial_e_scalar - _radial_k_scalar
    #print(q, _radial_sum, _radial_sum * k2)
    #radial_integral = -cel(q, 1, _radial_sum, _radial_sum * k2)
    K = ellipk(k2)
    E = ellipe(k2)
    #radial_integral = -K + (_radial_e_scalar * E)

    # ----------#

    # OUTPUT
    #   assemble the zeta and rho components of the output
    # Correct the direction: E_rho points *inward* for rho < ring radius
    sign = -1 if t_rho < 1 else 1
    frho = qk * (t_zeta / t_rho * sd) * (-K + ((1 + p2 + z2) / ddm * E))

    fzeta = ((Q / (4 * np.pi**2 * epsilon_0 * sd)) *
      (K + ((1 - t_rho**2 - t_zeta**2) / ddm) * E))

    return (frho, fzeta)

if __name__ == "__main__":
    import functools
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper

    @deco
    def test_fwysr():
        """
            Q: the total charge of the ring
            radius: the radius of the ring
            target_point: the point to evaluate the e-field at. assumed to be in cyl coordinates
            """
        # dimensionless
        Q = 1e-11
        radius =1.0
        z = 0.01
        target_point = (0, 0)
        rhos = [0.1, 0.5, 0.9, 0.99999, 1, 1.00001, 1.1, 1.5]

        for rho in rhos:
            # CONSTANTS
            #   save the target point as its base parts
            epsilon_0 = 8.854187817e-12  # Vacuum permittivity (F/m)
            t_rho = rho
            # if math.isclose(1.0, t_rho, rel_tol = 1e-10 ,abs_tol=1e-2):
            #    print(t_rho)
            #    t_rho = 1.1
            t_zeta = z
            #   q stuff
            qk = Q / (4 * np.pi ** 2 * epsilon_0)
            #   etc values that are used in the calculations, done here to avoid repeat
            a2 = 1
            p2 = t_rho ** 2
            z2 = t_zeta ** 2
            k2 = (4 * t_rho) / ((t_rho + 1) ** 2 + t_zeta ** 2)

            # ----------#

            # INTEGRALS
            # cel arguments for sum of elliptical integrals:
            #   aK(m) + bE(m) = cel(sqrt(1-m^2), 1, a + b, a + b(1-m^2))
            # gather radial parameters for cel
            ddm = ((1 - t_rho) ** 2 + z2)
            sd = np.sqrt((t_rho + 1) ** 2 + t_zeta ** 2)  # denominators of the scalars applied to the integrals
            #   scalars for the second and first kinds
            # _radial_e_scalar = (1 + p2 + z2) / ddm # 2nd
            # _radial_k_scalar = 1 # 1st
            # _radial_sum = _radial_e_scalar - _radial_k_scalar
            # print(q, _radial_sum, _radial_sum * k2)
            # radial_integral = -cel(q, 1, _radial_sum, _radial_sum * k2)
            K = ellipk(k2)
            E = ellipe(k2)
            # radial_integral = -K + (_radial_e_scalar * E)

            # ----------#

            # OUTPUT
            #   assemble the zeta and rho components of the output
            # Correct the direction: E_rho points *inward* for rho < ring radius
            sign = -1 if t_rho < 1 else 1
            frho = sign * qk * (t_zeta / t_rho * sd) * (-K + ((1 + p2 + z2) / ddm * E))

            fzeta = ((Q / (4 * np.pi ** 2 * epsilon_0 * sd)) *
                     (K + ((1 - t_rho ** 2 - t_zeta ** 2) / ddm) * E))
            print(
                f"rho={rho:.2f}, k2={k2:.4f}, K={K:.4f}, E={E:.4f}, E_rho={frho:.4f}, E_zeta={fzeta:.4f}")
        return (frho, fzeta)

    """qk = 1e-11 / np.pi * coulomb
    for r in [0.1, 0.5, 0.9, 1.1, 1.5]:
        p2 = r ** 2
        z2 = 0
        denominator = (1 - r) ** 2 + z2
        denominator_k = (1 + r) ** 2 + z2
        prefactor = r / np.sqrt(denominator)
        k2 = (4 * r) / denominator_k
        K = ellipk(k2)
        E = ellipe(k2)
        sign = -1 if r < 1 else 1
        radial_integral = -K + ((1 + p2 + z2) / denominator) * E
        frho = sign * qk * prefactor * radial_integral
        print(
            f"rho={r:.2f}, k2={k2:.4f}, K={K:.4f}, E={E:.4f}, radial_integral={radial_integral:.4f}, E_rho={frho:.4f}")
    """
    test_fwysr()